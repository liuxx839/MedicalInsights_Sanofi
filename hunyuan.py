import os
import json
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.sts.v20180813 import sts_client, models as sts_models
from tencentcloud.hunyuan.v20230901 import hunyuan_client, models
from tencentcloud.common.profile.client_profile import ClientProfile

class Hunyuan:
    def __init__(self, api_id=None, api_key=None):
        self.secret_id = api_id or os.environ.get("TENCENT_SECRET_ID")
        self.secret_key = api_key or os.environ.get("TENCENT_SECRET_KEY")
        
        if not self.secret_id or not self.secret_key:
            raise ValueError("API ID (Secret ID) and API Key (Secret Key) must be provided either as arguments or environment variables")
        
        self.chat = self.Chat(self)

    def get_temporary_credentials(self):
        try:
            cred = credential.Credential(self.secret_id, self.secret_key)
            client = sts_client.StsClient(cred, "ap-guangzhou")
            req = sts_models.AssumeRoleRequest()
            req.RoleArn = "qcs::cam::uin/100013736235:roleName/hunyuan_rw"
            req.RoleSessionName = "eim_dev_Hunyuan"
            resp = client.AssumeRole(req)
            
            resp_dict = json.loads(resp.to_json_string())
            credentials = resp_dict['Credentials']
            
            return {
                'TmpSecretId': credentials['TmpSecretId'],
                'TmpSecretKey': credentials['TmpSecretKey'],
                'Token': credentials['Token']
            }
        except TencentCloudSDKException as err:
            print(f"获取临时凭证失败: {err}")
            return None

    class Chat:
        def __init__(self, outer):
            self.outer = outer
            self.completions = self.Completions(outer)

        class Completions:
            def __init__(self, outer):
                self.outer = outer

            def create(self, model, messages, temperature=0.1, max_tokens=300):
                temp_credentials = self.outer.get_temporary_credentials()
                if not temp_credentials:
                    raise Exception("Failed to obtain temporary credentials")

                cred = credential.Credential(
                    temp_credentials['TmpSecretId'],
                    temp_credentials['TmpSecretKey'],
                    temp_credentials['Token']
                )
                cpf = ClientProfile()
                cpf.httpProfile.pre_conn_pool_size = 3
                client = hunyuan_client.HunyuanClient(cred, "ap-guangzhou", cpf)

                req = models.ChatCompletionsRequest()
                req.Messages = []
                for msg in messages:
                    message = models.Message()
                    message.Role = msg["role"]
                    message.Content = msg["content"]
                    req.Messages.append(message)

                req.Stream = False
                req.Model = model
                req.Temperature = temperature
                # req.MaxTokens = max_tokens

                try:
                    resp = client.ChatCompletions(req)
                    if resp.Choices:
                        return {
                            'choices': [{
                                'message': {
                                    'content': resp.Choices[0].Message.Content
                                }
                            }]
                        }
                    else:
                        return {'choices': []}
                except TencentCloudSDKException as e:
                    print(f"调用混元大模型失败: {e}")
                    return None

