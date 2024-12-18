class Embedder:
    def __init__(self):
        # Previous initialization remains the same
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.input_folder = os.path.join(self.base_path, "pdf_folder")
        self.output_folder_base = os.path.join(self.base_path, "embeddings")
        
        load_dotenv()
        
        self.embeddings = UpstageEmbeddings(
            model="solar-embedding-1-large-passage",
            api_key=os.getenv("UPSTAGE_API_KEY")
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=100,
            length_function=len,
        )
        
        os.makedirs(self.output_folder_base, exist_ok=True)
        
        # Add product types
        self.product_types = ['예금', '적금']
        self.retrievers = {}

    def get_retriever(self, product_type, source_type=None):
        """
        Get retriever for specific product type and source
        
        Args:
            product_type (str): '예금' or '적금'
            source_type (str, optional): 'pdf', 'df', or None for both
            
        Returns:
            retriever or dict of retrievers
        """
        if product_type not in self.product_types:
            raise ValueError(f"Invalid product type. Must be one of {self.product_types}")

        if source_type and source_type not in ['pdf', 'df']:
            raise ValueError("Source type must be 'pdf' or 'df'")
        
        # Create key for retrievers dictionary
        key = f"{product_type}_{source_type}" if source_type else product_type
        
        # If retriever already exists, return it
        if key in self.retrievers:
            return self.retrievers[key]

        # Load appropriate vector store(s)
        if source_type:
            persist_path = os.path.join(
                self.output_folder_base, 
                f"{product_type}_{source_type}"
            )
            vector_store = Chroma(
                persist_directory=persist_path,
                embedding_function=self.embeddings
            )
            retriever = vector_store.as_retriever(search_kwargs={"k": 3})
            self.retrievers[key] = retriever
            return retriever
        else:
            # Return both PDF and DataFrame retrievers for the product type
            pdf_retriever = self.get_retriever(product_type, 'pdf')
            df_retriever = self.get_retriever(product_type, 'df')
            return {'pdf': pdf_retriever, 'df': df_retriever}

    def create_all_embeddings(self):
        """Create embeddings for all product types"""
        for product_type in self.product_types:
            print(f"\nProcessing {product_type}...")
            
            # Create PDF embeddings
            try:
                self.store_pdf_embeds(product_type)
            except Exception as e:
                print(f"Error creating PDF embeddings for {product_type}: {str(e)}")

            # Create DataFrame embeddings
            try:
                df = pd.read_csv(os.path.join(self.base_path, 'src', 'data', 'Financial_products.csv'))
                filtered_df = df[df['상품유형'].str.contains(product_type, na=False)]
                self.store_df_embeds(filtered_df, product_type)
            except Exception as e:
                print(f"Error creating DataFrame embeddings for {product_type}: {str(e)}")


def main():
    try:
        # Initialize embedder
        embedder = Embedder()
        
        # Create embeddings for all product types
        embedder.create_all_embeddings()
        
        # Example of getting retrievers
        retrievers = {}
        for product_type in ['예금', '적금']:
            retrievers[product_type] = {
                'pdf': embedder.get_retriever(product_type, 'pdf'),
                'df': embedder.get_retriever(product_type, 'df')
            }
            
        print("\nRetrievers created successfully for all product types")
        return retrievers
        
    except Exception as e:
        print(f"Error in main: {str(e)}")
        return None

if __name__ == "__main__":
    retrievers = main()

class Embedder:
    def __init__(self):
        # Previous initialization same as before
        ...
        
        # Add product type mappings
        self.product_mappings = {
            '예금': 'Financial_products_deposit.csv',
            '적금': 'Financial_products_saving.csv'
        }
        self.retrievers = {}

    def load_bank_mapping(self, product_type):
        """
        Load bank mapping for specific product type
        """
        csv_filename = self.product_mappings.get(product_type)
        if not csv_filename:
            raise ValueError(f"Invalid product type: {product_type}")
            
        data_path = os.path.join(self.base_path, 'src', 'data', csv_filename)
        try:
            df = pd.read_csv(data_path)
            return df.set_index('상품명')['은행명'].to_dict()
        except Exception as e:
            print(f"Error loading bank mapping for {product_type}: {str(e)}")
            return {}

    def create_all_embeddings(self):
        """Create embeddings for all product types"""
        for product_type, csv_filename in self.product_mappings.items():
            print(f"\nProcessing {product_type}...")
            
            # Load bank mapping for this product type
            self.bank_mapping = self.load_bank_mapping(product_type)
            
            # Create PDF embeddings
            try:
                self.store_pdf_embeds(product_type)
            except Exception as e:
                print(f"Error creating PDF embeddings for {product_type}: {str(e)}")

            # Create DataFrame embeddings
            try:
                csv_path = os.path.join(self.base_path, 'src', 'data', csv_filename)
                df = pd.read_csv(csv_path)
                self.store_df_embeds(df, product_type)
                print(f"Created embeddings for {product_type} from {csv_filename}")
            except Exception as e:
                print(f"Error creating DataFrame embeddings for {product_type}: {str(e)}")

    def get_retriever(self, product_type, source_type=None):
        """Same as before but with product type validation"""
        if product_type not in self.product_mappings:
            raise ValueError(f"Invalid product type. Must be one of {list(self.product_mappings.keys())}")
        
        # Rest of the method remains the same
        ...

def main():
    try:
        print("Initializing Embedder...")
        embedder = Embedder()
        
        print("Creating embeddings for all product types...")
        embedder.create_all_embeddings()
        
        # Create retrievers for each product type
        retrievers = {}
        for product_type in embedder.product_mappings.keys():
            print(f"\nCreating retrievers for {product_type}...")
            retrievers[product_type] = {
                'pdf': embedder.get_retriever(product_type, 'pdf'),
                'df': embedder.get_retriever(product_type, 'df')
            }
            
        print("\nAll retrievers created successfully")
        return retrievers
        
    except Exception as e:
        print(f"Error in main: {str(e)}")
        return None
    
    def __init__(self):
    """
    Initialize the Embedder
    """
    # Get the current directory (modules)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Go up to src directory
    src_dir = os.path.dirname(current_dir)
    
    # Set paths
    self.base_path = src_dir  # src directory
    self.data_path = os.path.join(self.base_path, 'data')
    self.input_folder = os.path.join(self.base_path, "pdf_folder")
    self.output_folder_base = os.path.join(self.base_path, "embeddings")
    
    # Add product type mappings with correct filenames
    self.product_mappings = {
        '예금': 'Financial_products_deposit.csv',
        '적금': 'Financial_products_savings.csv'  # Note the corrected filename
    }
    
    load_dotenv()
    
    self.embeddings = UpstageEmbeddings(
        model="solar-embedding-1-large-passage",
        api_key=os.getenv("UPSTAGE_API_KEY")
    )
    
    self.text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=100,
        length_function=len,
    )
    
    os.makedirs(self.output_folder_base, exist_ok=True)
    self.retrievers = {}

def load_bank_mapping(self, product_type):
    """
    Load bank mapping for specific product type
    """
    csv_filename = self.product_mappings.get(product_type)
    if not csv_filename:
        raise ValueError(f"Invalid product type: {product_type}")
        
    data_path = os.path.join(self.data_path, csv_filename)
    print(f"Loading from: {data_path}")  # Debug print
    
    try:
        df = pd.read_csv(data_path)
        return df.set_index('상품명')['은행명'].to_dict()
    except Exception as e:
        print(f"Error loading bank mapping for {product_type}: {str(e)}")
        return {}