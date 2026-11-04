"""Optional: save reports to IBM Cloud Object Storage (Lite plan)."""
import os


def save_to_cos(key: str, content: str) -> str:
    import ibm_boto3
    from ibm_botocore.client import Config

    cos = ibm_boto3.client(
        "s3",
        ibm_api_key_id=os.environ["COS_API_KEY"],
        ibm_service_instance_id=os.environ["COS_INSTANCE_CRN"],
        config=Config(signature_version="oauth"),
        endpoint_url=os.environ["COS_ENDPOINT"],
    )
    cos.put_object(Bucket=os.environ["COS_BUCKET"], Key=key, Body=content.encode("utf-8"))
    return f"cos://{os.environ['COS_BUCKET']}/{key}"
