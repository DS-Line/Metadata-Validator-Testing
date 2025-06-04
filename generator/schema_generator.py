from simple_ddl_parser import DDLParser
from pyvalidator.format_validator import GeneratedSchema
from typing import Dict, List
import yaml
# from decouple import config
from google import genai
from dotenv import load_dotenv
import os
import time
from google.genai.errors import ClientError


# config = Config('.env')




class SchemaGenerator():
    
    load_dotenv()
    GEMINI_API_KEY = os.getenv("API_KEY")
    MODEL = os.getenv("MODEL")
    
    
    def __init__(self):
        self.schema = None
        self.llm = genai.Client(api_key=self.GEMINI_API_KEY)
        
        
    def generate_subject_area_prompt(self, table_name: str, column_names: list[str], column_descriptions: list[str]) -> str:
        column_info = "\n".join(
            f"- {name}: {desc}" for name, desc in zip(column_names, column_descriptions)
        )

        return f"""You are a data analyst. Based on the column names and their descriptions, infer a concise subject area for the table.
        
                Table: {table_name}

                Columns:
                {column_info}

                Instructions:
                - Output a subject area that summarizes the purpose or theme of the table.
                - Use 2 to 5 lowercase words.
                - Do not include the word "table".
                - Be specific and domain-relevant.

                Respond with only the subject area label."""
                
                

                    
    def generate_column_description_prompt(self, column_name: str, table_name: str, data_type: str) -> str:
        return f"""You are a data analyst. Provide a brief description (5-12 words) for a database column.
        
    Table: {table_name}
    Column: {column_name}
    Data Type: {data_type}
    

    What does this column likely represent? Respond with only the description."""

    
    def generate_content(self, prompt:str, delay = 60, retires = 3) -> str:
        # prompt = self.generate_column_description_prompt(prompt)
        if retires == 0 :
            raise ValueError(f"Retries exhausted")
        try:
            response = self.llm.models.generate_content(
                model=self.MODEL, contents=prompt
            )
        except ClientError as e:
            if e.code == 429:
                print(f"Quota exceeded, retyring in {delay} seconds ...")
                time.sleep(delay)
                return self.generate_content(prompt, retires= retires -1)
            else:
                raise e
        return response.text.replace('"','').strip()
    
        
    def generate(self, ddl: str) -> Dict[str,GeneratedSchema]:
        
        parsed_ddl = DDLParser(ddl).run(output_mode="hql")
        result ={}
        
        for table_dict in parsed_ddl:
            if "table_name" not in table_dict:
                continue
            print(table_dict)
            table_name = table_dict["table_name"]
            joins = []
            columns = []
            
            if table_dict["primary_key"] != []:
                primary_key = table_dict["primary_key"][0]
            else:
                primary_key = ""
            
            for col in table_dict["columns"]:
                column = col["name"]
                type = col["type"]
                if "comment" in col and col["comment"]:
                    desc = col["comment"]
                else:
                    prompt = self.generate_column_description_prompt(column_name=column,table_name=table_name,data_type=type)
                    desc = self.generate_content(prompt)
                    
                if "references" in col and col["references"]:   
                    foreign_key = True
                    reference_table = col["references"].get("table")
                    reference_col = col["references"].get("column")
                    join_condition = f"{table_name}.{column} = {reference_table}.{reference_col}"
                    joins.append(join_condition)
                else:
                    foreign_key = False
                    
                # if "contraints" in col and col["contraints"]:
                #     if "references" in col["contraints"] and col["contraints"].get("references"):
                #         references = col["contraints"].get("references")
                #         for reference in references:
                #             foreign_key = True
                #             reference_table = reference["references"].get("table")
                #             reference_col = reference["references"].get("columns")[0]
                #             join_condition = f"{table_name}.{column} = {reference_table}.{reference_col}"
                #             joins.append(join_condition)
                        
                                    
                columns.append(
                    {
                        "name": column,
                        "type": type,
                        "column": column,
                        "desc": desc,
                        "primary_key": (column == primary_key),
                        "foreign_key": foreign_key
                    }
                )
                
            subject_area_prompt = self.generate_subject_area_prompt(table_name=table_name,column_names=[col["name"] for col in columns],column_descriptions=[col["desc"] for col in columns])
                
            table_schema = GeneratedSchema(
                subject_area= self.generate_content(subject_area_prompt),
                table_info= [{
                    "table": table_name,
                    "joins": joins,
                }],
                columns = {col["column"]: col for col in columns}
            )
            

            print(table_schema)
        
            result[table_name] = table_schema
            
        return result

        
                