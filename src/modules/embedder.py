import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import os
import tempfile
from langchain_upstage import UpstageEmbeddings
from langchain_community.document_loaders import PyPDFLoader, CSVLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv


class Embedder:

    def __init__(self, input_folder="pdf_folder", output_folder_base="embeddings"):
        """
        금융 상품 관련 문서 임베딩 생성 및 저장
        """
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.input_folder = os.path.join(base_path, input_folder)
        self.output_folder_base = os.path.join(base_path, output_folder_base)

        # 환경 변수 파일 로드
        load_dotenv()
        UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")

        if UPSTAGE_API_KEY is None:
            raise ValueError("UPSTAGE_API_KEY environment variable not found.")

        # Upstage Embedding Model 설정
        self.embeddings = UpstageEmbeddings(model="solar-embedding-1-large-passage", 
                                            upstage_api_key=UPSTAGE_API_KEY)

    def get_embedding_function(self):
        """
        임베딩 생성 모델 반환
        """
        return self.embeddings

    def create_embeddings_dir(self, product_type):
        """
        상품 종류에 따른 임베딩 디렉토리 생성
        """
        path = os.path.join(self.output_folder_base, product_type)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def store_doc_embeds(self, file, original_filename, selected_type, metadata=None):
        """
        주어진 파일로부터 문서 임베딩을 생성 및 저장
        """
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as tmp_file:
            tmp_file.write(file)
            tmp_file_path = tmp_file.name

        # 텍스트를 일정 크기로 나누는 TextSplitter 설정
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000, 
            chunk_overlap=100,
            length_function=len,
        )

        # 파일 확장자에 따라 로더 선택
        file_extension = os.path.splitext(original_filename)[1].lower()
        if file_extension == ".csv":
            loader = CSVLoader(file_path=tmp_file_path, encoding="utf-8", csv_args={'delimiter': ','})
            data = loader.load()
        elif file_extension == ".pdf":
            loader = PyPDFLoader(file_path=tmp_file_path)
            data = loader.load_and_split(text_splitter)
        elif file_extension == ".txt":
            loader = TextLoader(file_path=tmp_file_path, encoding="utf-8")
            data = loader.load_and_split(text_splitter)
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")

        # 임시 파일 삭제
        os.remove(tmp_file_path)

        # 상품 종류에 따른 디렉토리 생성
        persist_path = self.create_embeddings_dir(selected_type)

        # 각 chunk에 메타데이터 추가
        documents_with_metadata = [
            {
                "page_content": doc.page_content,
                "metadata": metadata or {}
            }
            for doc in data
        ]

        # Chroma DB에 임베딩 저장
        vector_store = Chroma.from_documents(
            documents=documents_with_metadata,
            ids=[doc["page_content"] for doc in documents_with_metadata],
            embedding=self.get_embedding_function(),
            persist_directory=persist_path
        )
        vector_store.persist()

    def store_embeddings_from_folder(self, product_type, metadata=None):
        """
        폴더별 파일 임베딩 생성 및 저장
        """
        product_folders = []

        # 예금 & 적금의 경우, 두 폴더 처리
        if product_type == '예금 & 적금':
            product_folders.append(os.path.join(self.input_folder, '예금'))
            product_folders.append(os.path.join(self.input_folder, '적금'))
        else:
            product_folders.append(os.path.join(self.input_folder, product_type))

        for folder in product_folders:
            if not os.path.exists(folder):
                print(f"Folder {folder} does not exist.")
                continue

            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)

                if filename.lower().endswith(".pdf"):
                    with open(file_path, "rb") as file:
                        file_content = file.read()
                        self.store_doc_embeds(file_content, filename, product_type, metadata)

    def get_retriever(self, product_type='예금 & 적금', filters=None):
        """
        주어진 상품 유형과 조건에 맞는 벡터 스토어 리트리버 반환
        """
        persist_path = os.path.join(self.output_folder_base, product_type)
        vector_store = Chroma(
            persist_directory=persist_path,
            embedding_function=self.get_embedding_function()
        )

        retriever = vector_store.as_retriever()
        
        # 필터를 적용해 리트리버 설정
        if filters:
            retriever.search_kwargs["filters"] = filters

        print(f"Retriever for {product_type} with filters: {filters}")
        return retriever

    def list_embeddings(self, product_type):
        """
        지정된 폴더에 저장된 모든 임베딩 파일을 출력
        """
        persist_path = os.path.join(self.output_folder_base, product_type)
        print(f"Listing stored embeddings in {persist_path}:")
        
        for root, dirs, files in os.walk(persist_path):
            for file in files:
                print(f"File: {file}, Path: {os.path.join(root, file)}")


# 직접 실행 시, PDF 폴더에서 임베딩 생성
if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))
    input_folder = os.path.join(base_path, "pdf_folder")
    output_folder = os.path.join(base_path, "embeddings")

    embedder = Embedder(input_folder=input_folder, output_folder_base=output_folder)

    # 예금, 적금 임베딩 생성
    embedder.store_embeddings_from_folder('예금', metadata={"product_type": "예금"})
    embedder.store_embeddings_from_folder('적금', metadata={"product_type": "적금"})
    embedder.store_embeddings_from_folder('예금 & 적금', metadata={"product_type": "예금 & 적금"})

    # 저장된 임베딩 확인
    embedder.list_embeddings('예금')
    embedder.list_embeddings('적금')
    embedder.list_embeddings('예금 & 적금')
