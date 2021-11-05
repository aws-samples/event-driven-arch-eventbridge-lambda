## event-driven-architecture-using-s3-event-notifications

**[Feature request](https://github.com/aws-samples/event-driven-architecture-using-s3-event-notifications/issues/new)** | **[Detailed blog post](https://aws.amazon.com/blogs/<TBD>)**

This sample application showcases how to set up and use [Amazon S3 Event Notifications](https://docs.aws.amazon.com/AmazonS3/latest/userguide/NotificationHowTo.html) and 
[Amazon Lambda](https://aws.amazon.com/lambda/) to create an event-driven serverless architecture able to process files and archive such files properly.

This example is composed by two applications:  
* An external service application [simulator](simulador/main.go). It runs into an EC2 instance, and is written in Golang.  
* A [lambda function](integration-lambda/app.py) written in python, which will process the files received at a predefined lambda repository.
This SAM app uses java as language runtime for the lambda functions and custom resources.  

All resources are deployed trought the Cloudformation located at (template.yml)[`template.yml`].

# Setup 

The main template [template.yml](template.yml) is used to set up all moving parts of the stack, including EC2 instance, security groups, IAM roles and HTTP API and different types of auth mentioned above.

```
aws cloudformation deploy --stack-name event-driven-architecture --template-file template.yml --capabilities CAPABILITY_IAM

Waiting for changeset to be created..
Waiting for stack create/update to complete
Successfully created/updated stack - event-driven-architecture
```

You can also customize the following parameters on template call:

`BucketNameLeituras` - bucket to upload your example files.  
`BucketNameLeiturasCorretas` - bucket that will receive files processed with success.  
`BucketNameLeiturasIncorretas` - bucket that will receive files processed NOT successfully.  

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## Requirements

* AWS CLI already configured with Administrator permission

## License

This library is licensed under the MIT-0 License. See the LICENSE file.