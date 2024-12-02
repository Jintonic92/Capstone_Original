import os
import pandas as pd
from langchain_upstage import ChatUpstage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.output_parsers import PydanticOutputParser
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_upstage import UpstageGroundednessCheck
from pydantic import BaseModel, Field
from string import Template
import yaml
from typing import Optional


load_dotenv()

class Chatbot:
    """
    통합 금융 챗봇 구현
    사용자의 게좌 정보 조회
    맞춤형 금융 상품 추천 및 이자 계산 
    금융 상식 질의문답 수행
    """
    UPSTAGE_API_KEY = os.getenv('UPSTAGE_API_KEY')

    # 유효한 은행명과 상품명을 정의하여 Hallucination 방지 
    predefined_valid_banks = ["NH농협은행", "하나은행", "우리은행", "KB국민은행", "토스은행", "신한은행", "카카오뱅크", "SBI저축은행", "K뱅크"]
    predefined_valid_products = ["행복 knowhow 연금예금", "트래블로그 여행 적금", "정기예금", "급여하나 월복리 적금", "NH직장인월복리적금", "NH장병내일준비적금", "NH올원e예금", "NH더하고나눔정기예금", "NH내가Green초록세상예금", 
                                 "WON플러스 예금", "WON 적금", "N일 적금(31일)", "우리 SUPER주거래 적금", "우리 첫거래우대 정기예금", "KB 국민 UP 정기예금", "KB 내맘대로적금", "KB 스타적금", "KB 장병내일준비적금", "직장인우대적금", 
                                 "KB Star 정기예금", "토스뱅크 굴비 적금", "토스뱅크 먼저 이자 받는 정기예금", "토스뱅크 자유 적금", "토스뱅크 키워봐요 적금", "Tops CD연동정기예금", "쏠편한 정기예금", "신한 My플러스 정기예금", 
                                 "미래설계 장기플랜 연금예금", "미래설계 크레바스 연금예금", "카카오뱅크 정기예금", "희망정기적금", "적립식예금", "희망정기적금", "회전정기예금", "정기적금", "정기예금", "자유적립예금", "적립식예금", 
                                 "자유적금", "손주사랑정기적금", "거치식예금", "코드K정기예금", "코드K 자유적금", "주거래우대자유적금"]

    # 불용어 목록 추가 (예: '정기')
    ignore_words = ['정기']

    def __init__(self, retriever_예금, retriever_적금, retriever_예금_적금, data=None): 
        """
        Chatbot 클래스 초기화
        """
        self.llm = ChatUpstage(api_key=self.UPSTAGE_API_KEY, temperature=0.0)
        self.retriever_예금 = retriever_예금
        self.retriever_적금 = retriever_적금
        self.retriever_예금_적금 = retriever_예금_적금
        self.retriever = None

        # QA 프롬프트 로드
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.prompts_path = os.path.join(self.base_path, 'src', 'modules', 'prompts')
        self.qa_system_template_path = os.path.join(self.prompts_path, 'qa_system.yaml')
        self.qa_system_template = self.load_yaml(self.qa_system_template_path)['template']
        self.qa_system_prompt = Template(self.qa_system_template)

        # 데이터 로드
        if data is None:
            self.data_path = os.path.join(self.base_path, 'src', 'data', 'mydata_dummy.csv')
        else:
            self.data_path = os.path.join(self.base_path, data)
        
        self.user_data = pd.read_csv(self.data_path)

    def load_yaml(self, path):
        """
        YAML 파일을 로드
        """
        try:
            with open(path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Error: {path} 경로에 파일이 없습니다.")
            return {}

    def clean_text(self, text):
        """
        공백 제거 및 불용어 삭제
        """
        cleaned_text = ''.join(text.split())
        for word in self.ignore_words:
            cleaned_text = cleaned_text.replace(word, '')
        return cleaned_text     

    def retrieve_documents(self, query, target_period, keywords, product_type='적용안함', top_k=3):
        """
        사용자가 입력한 쿼리를 기반으로 관련 문서 검색
        """
        self.set_retriever_by_product_type(product_type)
        filters = {
            "target_period": target_period,
            "keywords": keywords
        }
        if self.retriever:
            search_result = self.retriever.invoke(query, top_k=top_k, filters=filters)
            if not search_result:
                return None
            extracted_texts = [BeautifulSoup(search.page_content, "html.parser").get_text(separator="\n") for search in search_result]
            return "\n".join(extracted_texts)
        else:
            return None

    def generate_responses(self, question, context, chat_history, target_period, keywords, product_type='적용안함'):
        """
        사용자가 입력한 질문에 대한 응답 생성
        """
        prompt = self.build_prompt(context, question, target_period, keywords, product_type)
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ])
        chain = qa_prompt | self.llm | StrOutputParser()
        response = chain.invoke({
            "input": question,
            "context": context,
            "chat_history": chat_history
        })
        return response

    def build_prompt(self, context, question, target_period, keywords, product_type):
        """
        질문에 따른 프롬프트를 생성
        """
        full_prompt = self.qa_system_prompt.safe_substitute(
            format="",
            context=context
        )
        full_prompt += f"\n사용자가 입력한 정보:\n기간: {target_period}, 키워드: {keywords}, 상품 타입: {product_type}\n"
        full_prompt += f"질문: {question}\n응답:"
        return full_prompt

    def set_retriever_by_product_type(self, product_type):
        """
        금융 상품 종류에 맞는 리트리버 설정
        """
        if product_type == '예금':
            self.retriever = self.retriever_예금
        elif product_type == '적금':
            self.retriever = self.retriever_적금
        else:
            self.retriever = self.retriever_예금_적금
