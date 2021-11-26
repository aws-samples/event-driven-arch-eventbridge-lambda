## event-driven-architecture-using-s3-event-notifications

**[Feature request](https://github.com/aws-samples/event-driven-architecture-using-s3-event-notifications/issues/new)** | **[Detailed blog post](https://aws.amazon.com/blogs/<TBD>)**

This sample application showcases how to set up and use [Amazon S3 Event Notifications](https://docs.aws.amazon.com/AmazonS3/latest/userguide/NotificationHowTo.html) and 
[Amazon Lambda](https://aws.amazon.com/lambda/) to create an event-driven serverless architecture able to process files and archive such files properly.

This example is composed by two applications:  
* An application that runs on Amazon EC2 instance, simulating an external integration - [simulator](simulador/main.go). It is written in GoLang and optimized to run on EC2 with [Amazon Graviton Processors](https://aws.amazon.com/ec2/graviton/)
* A [lambda function](integration-lambda/app.py) written in python, which will process the files received at a predefined lambda repository.

All resources are deployed trought the [AWS Cloudformation](https://aws.amazon.com/cloudformation/) template located at [`template.yml`](template.yml).

# Setup 

The main template [template.yml](template.yml) is used to set up all moving parts of the stack, including EC2 instance, simulator, and security groups mentioned above.

```
aws cloudformation deploy --stack-name event-driven-architecture --template-file template.yml --capabilities CAPABILITY_IAM

Waiting for changeset to be created..
Waiting for stack create/update to complete
Successfully created/updated stack - event-driven-architecture
```

You can also customize the following parameters on template call:

`BucketNameEntrada` - bucket to upload your example files.  
`BucketNameProcessamentoSucesso` - bucket that will receive files processed with success.  
`BucketNameProcessamentoErro` - bucket that will receive files processed NOT successfully.  

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## Requirements

* AWS CLI already configured with Administrator permission

## License

This library is licensed under the MIT-0 License. See the LICENSE file.