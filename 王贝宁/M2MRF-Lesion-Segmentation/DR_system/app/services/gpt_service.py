import os
import openai
from flask import current_app

class GPTService:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        openai.api_key = self.api_key

    def generate_health_advice(self, lesion_info):
        """
        根据病灶信息生成健康建议
        :param lesion_info: 病灶信息字典，包含病灶类型、数量等
        :return: 生成的健康建议
        """
        try:
            # 构建提示词
            prompt = self._build_prompt(lesion_info)
            
            # 调用GPT API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个专业的眼科医生，请根据患者的眼底图像分析结果，给出专业的健康建议。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # 提取生成的建议
            advice = response.choices[0].message.content.strip()
            return advice
            
        except Exception as e:
            current_app.logger.error(f"GPT API调用失败: {str(e)}")
            return "暂时无法生成健康建议，请稍后再试。"

    def _build_prompt(self, lesion_info):
        """
        构建提示词
        :param lesion_info: 病灶信息
        :return: 格式化的提示词
        """
        if not lesion_info or lesion_info.get('lesion_count', 0) == 0:
            return "患者眼底图像未检测到病灶，请给出日常护眼建议。"
        
        prompt = f"患者眼底图像检测到{lesion_info['lesion_count']}个病灶。"
        
        prompt += "\n请根据以上信息，给出专业的健康建议，包括：\n"
        prompt += "1. 对当前情况的简要说明\n"
        prompt += "2. 具体的治疗建议\n"
        prompt += "3. 日常注意事项\n"
        prompt += "4. 建议的复查时间"
        
        return prompt 