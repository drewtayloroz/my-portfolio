import boto3
from botocore.client import Config
import StringIO
import zipfile



def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-west-1:985130161678:deployPortfolioTopic')

    try:
        s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))

        portfolio_bucket = s3.Bucket('portfolio.drewtaylor.name')
        build_bucket = s3.Bucket('portfoliobuild.drewtaylor.name')

        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm)
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
        print "Job done!"
        topic.publish(Subject="Portfolio Deploy Successfully", Message="Portfolio deployed succesfully!")
    except:
        topic.publish(Subject="Portfolio Deploy Failed", Message="Portfolio WAS NOT deployed successfully!")
        raise

    return 'Hello from Lambda'
