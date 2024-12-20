import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import os
import tempfile
import pandas as pd
import sys
from langchain_upstage import UpstageEmbeddings
from langchain_community.document_loaders import PyPDFLoader, CSVLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain.schema import Document

class Embedder:
   def __init__(self):
       """
       임베딩을 생성하고 저장하는 클래스
       - PDF 문서와 DataFrame을 처리하여 임베딩을 생성
       - 생성된 임베딩은 지정된 디렉토리에 저장됨
       """
       # 기본 경로 설정
       self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
       self.data_path = os.path.join(self.base_path, 'src', 'data')
       self.input_folder = os.path.join(self.base_path, "src", "modules", "pdf_folder")
       self.output_folder_base = os.path.join(self.base_path, "src", "modules", "embeddings")
       
       # 상품 유형별 CSV 파일 매핑
       self.product_mappings = {
           '예금': 'Financial_products_deposit.csv',
           '적금': 'Financial_products_savings.csv'
       }
       
       # 환경 변수 로드 및 임베딩 초기화
       load_dotenv()
       self.embeddings = UpstageEmbeddings(
           model="solar-embedding-1-large-passage",
           api_key=os.getenv("UPSTAGE_API_KEY")
       )
       
       # 텍스트 분할 설정
       self.text_splitter = RecursiveCharacterTextSplitter(
           chunk_size=2000,
           chunk_overlap=100,
           length_function=len,
       )
       
       # 출력 디렉토리 생성
       os.makedirs(self.output_folder_base, exist_ok=True)
       self.retrievers = {}

   def get_bank_name(self, product_name):
       """
       상품명으로 은행명 조회
       Args:
           product_name (str): 상품명
       Returns:
           str: 은행명 (매핑 정보가 없는 경우 'Unknown Bank' 반환)
       """
       if hasattr(self, 'bank_mapping'):
           return self.bank_mapping.get(product_name, 'Unknown Bank')
       return 'Unknown Bank'

   def load_bank_mapping(self, product_type):
       """상품 유형별 은행 매핑 정보 로드"""
       csv_filename = self.product_mappings.get(product_type)
       if not csv_filename:
           raise ValueError(f"Invalid product type: {product_type}")
       
       data_path = os.path.join(self.data_path, csv_filename)
       print(f"Loading bank mapping from: {data_path}")
       
       try:
           df = pd.read_csv(data_path)
           return df.set_index('상품명')['은행명'].to_dict()
       except Exception as e:
           print(f"Error loading bank mapping for {product_type}: {str(e)}")
           return {}

   def create_embeddings_dir(self, product_type):
       """상품 유형별 임베딩 저장 디렉토리 생성"""
       path = os.path.join(self.output_folder_base, product_type)
       os.makedirs(path, exist_ok=True)
       return path

   def store_pdf_embeds(self, product_type):
       """PDF 문서의 임베딩 생성 및 저장"""
       pdf_folder = os.path.join(self.input_folder, product_type)
       if not os.path.exists(pdf_folder):
           raise FileNotFoundError(f"PDF folder not found: {pdf_folder}")
           
       documents = []
       
       for filename in os.listdir(pdf_folder):
           if filename.endswith('.pdf'):
               print(f"Processing PDF: {filename}")
               file_path = os.path.join(pdf_folder, filename)
               loader = PyPDFLoader(file_path)
               pages = loader.load_and_split(self.text_splitter)
               
               product_name = filename.replace('.pdf', '')
               
               for page in pages:
                   page.metadata.update({
                       'product_name': product_name,
                       'product_type': product_type,
                       'source': filename,
                       'bank_name': self.get_bank_name(product_name)
                   })
               documents.extend(pages)

       if documents:
           persist_path = self.create_embeddings_dir(f"{product_type}_pdf")
           Chroma.from_documents(
               documents=documents,
               embedding=self.embeddings,
               persist_directory=persist_path,
               collection_metadata={"hnsw:space": "cosine"}
           )
           print(f"Stored {len(documents)} PDF embeddings for {product_type}")
       else:
           print(f"No PDF documents found for {product_type}")

   def store_df_embeds(self, product_type):
       """DataFrame의 임베딩 생성 및 저장"""
       csv_path = os.path.join(self.data_path, self.product_mappings[product_type])
       print(f"Loading DataFrame from: {csv_path}")
       
       try:
           df = pd.read_csv(csv_path)
           documents = []
           
           for _, row in df.iterrows():
               text = f"""
               상품명: {row['상품명']}
               은행명: {row['은행명']}
               상품유형: {row['상품유형']}
               가입대상: {row['가입대상']}
               최소납입금액: {row['최소납입금액']}
               최대납입금액: {row['최대납입금액']}
               계약기간: {row['계약기간']}
               금리: {row['금리']}
               우대이율 조건: {row['우대이율 조건']}
               """
               
               metadata = {
                   "source": "dataframe",
                   "product_name": row['상품명'],
                   "bank_name": row['은행명']
               }
               
               documents.append(Document(
                   page_content=text,
                   metadata=metadata
               ))
           
           persist_path = self.create_embeddings_dir(f"{product_type}_df")
           Chroma.from_documents(
               documents=documents,
               embedding=self.embeddings,
               persist_directory=persist_path
           )
           print(f"Stored {len(documents)} DataFrame embeddings for {product_type}")
           
       except Exception as e:
           print(f"Error processing DataFrame for {product_type}: {str(e)}")

   def check_embeddings_exist(self, product_type, source_type):  
       """임베딩이 이미 생성되어 있는지 확인"""
       persist_path = os.path.join(self.output_folder_base, f"{product_type}_{source_type}")
       return os.path.exists(persist_path)
   
   def create_all_embeddings(self):
       """모든 상품 유형의 임베딩 생성"""
       for product_type in self.product_mappings.keys():
           print(f"\nProcessing {product_type}...")
           
           # 은행 매핑 로드
           self.bank_mapping = self.load_bank_mapping(product_type)
           
           # PDF 임베딩 생성
           try:
               self.store_pdf_embeds(product_type)
           except Exception as e:
               print(f"Error creating PDF embeddings for {product_type}: {str(e)}")
               
           # DataFrame 임베딩 생성
           try:
               self.store_df_embeds(product_type)
           except Exception as e:
               print(f"Error creating DataFrame embeddings for {product_type}: {str(e)}")
    
   def get_retriever(self, product_type, source_type=None):
       """상품 유형별 retriever 반환"""
       if product_type not in self.product_mappings:
           raise ValueError(f"Invalid product type. Must be one of {list(self.product_mappings.keys())}")
        
       if source_type and source_type not in ['pdf', 'df']:
           raise ValueError("Source type must be 'pdf' or 'df'")
        
       key = f"{product_type}_{source_type}" if source_type else product_type
        
       if key in self.retrievers:
           return self.retrievers[key]
            
       if source_type:
           persist_path = self.create_embeddings_dir(f"{product_type}_{source_type}")
           print(f"Looking for embeddings at: {persist_path}")
            
           vector_store = Chroma(
                persist_directory=persist_path,
                embedding_function=self.embeddings
            )
           retriever = vector_store.as_retriever(search_kwargs={"k": 3})
           self.retrievers[key] = retriever
           return retriever
       else:
           return {
                'pdf': self.get_retriever(product_type, 'pdf'),
                'df': self.get_retriever(product_type, 'df')
            }

   
def main():
   try:
       print("Initializing Embedder...")
       embedder = Embedder()
       
       print("Creating embeddings for all product types...")
       embedder.create_all_embeddings()
       
       print("\nCreating retrievers...")
       retrievers = {}
       for product_type in embedder.product_mappings.keys():
           print(f"Creating retrievers for {product_type}...")
           retrievers[product_type] = embedder.get_retriever(product_type)
           
       print("All retrievers created successfully")
       return retrievers
       
   except Exception as e:
       print(f"Error in main: {str(e)}")
       return None

if __name__ == "__main__":
   retrievers = main()