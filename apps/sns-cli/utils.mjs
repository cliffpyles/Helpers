import {
  CloudFormationClient,
  CreateStackCommand,
  DescribeStacksCommand,
  waitUntilStackCreateComplete
} from '@aws-sdk/client-cloudformation'
import {
  CloudWatchLogsClient,
  DescribeLogGroupsCommand,
  GetLogEventsCommand
} from '@aws-sdk/client-cloudwatch-logs'
import {
  CreateTopicCommand,
  DeleteTopicCommand,
  GetTopicAttributesCommand,
  ListTopicsCommand,
  ListSubscriptionsByTopicCommand,
  PublishCommand,
  SNSClient
} from '@aws-sdk/client-sns'
import {
  SQSClient,
  CreateQueueCommand,
  GetQueueAttributesCommand,
  ReceiveMessageCommand
} from '@aws-sdk/client-sqs'
import { STSClient, GetCallerIdentityCommand } from '@aws-sdk/client-sts'
import Conf from 'conf'
import Table from 'cli-table3'
import { readFileSync } from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'
const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const config = new Conf({ projectName: 'sns-cli' })

const sts = new STSClient()
const currentUser = await sts.send(new GetCallerIdentityCommand({}))
const region = process.env.AWS_REGION || 'us-east-1'

config.set('region', region)
config.set('accountId', currentUser.Account)
config.set('username', currentUser.Arn.split('/').pop())

export const sns = new SNSClient({ region: config.get('region') })
export const sqs = new SQSClient({ region: config.get('region') })
export const cf = new CloudFormationClient({ region: config.get('region') })
export const cw = new CloudWatchLogsClient({ region: config.get('region') })

export function getTopicArn (topicName) {
  const topicPrefix = `arn:aws:sns:${config.get('region')}:${config.get(
    'accountId'
  )}`
  const topicArn = topicName.startsWith(topicPrefix)
    ? topicName
    : `${topicPrefix}:${topicName}`

  return topicArn
}

export function getTopicName (topicArn) {
  const topicPrefix = `arn:aws:sns:${config.get('region')}:${config.get(
    'accountId'
  )}`
  const topicName = topicArn.startsWith(topicPrefix)
    ? topicArn.split(':').at(-1)
    : topicArn

  return topicName
}

export async function stackExists (stackName) {
  try {
    const describeParams = { StackName: stackName }
    await cf.send(new DescribeStacksCommand(describeParams))

    return true
  } catch (err) {
    if (
      err.name === 'ValidationError' &&
      err.message.includes('does not exist')
    ) {
      return false // The stack does not exist
    } else {
      throw err // Rethrow the error
    }
  }
}

export async function getStackDetails (stackName) {
  try {
    const describeParams = { StackName: stackName }
    const stackDetails = await cf.send(
      new DescribeStacksCommand(describeParams)
    )

    return stackDetails.Stacks[0]
  } catch (err) {
    throw err
  }
}

export async function tailLogGroup(logGroupName, logStreamName){
  try {
    


    // Get the sequence token for the most recent log event
    const tokenParams = {
      logGroupName,
      logStreamName,
      startFromHead: true
    };
    // const tokenData = await cw.getQueryResults(tokenParams);
    const tokenData = await cw.send(new GetLogEventsCommand(tokenParams));
    const columns = new Set(tokenData.events.flatMap(event => Object.keys(event)))

    const table = new Table({
      head: [...columns]
    });
    // const sequenceToken = tokenData.results[0].data[0].value;

    // Tail the log group by continuously fetching new log events
    let nextToken = null;
    while (true) {
      const params = {
        logGroupName,
        logStreamName,
        nextToken,
        interleaved: true
      };
      const data = await cw.send(new GetLogEventsCommand(params));

      // Process the log events
      const events = data.events;
      for (const event of events) {
        // console.log(event.timestamp, event.message);
        // table.push(event.message);
        // console.log(table.toString());
        console.log(event.message)
      }
      // Get the next token to continue tailing the log group
      nextToken = data.nextForwardToken;
      // Wait for a short period of time before fetching more log events
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  } catch (err) {
    console.error(`Failed to tail log group: ${err}`);
  }
}

export async function createStack (params) {
  console.log(
    `creating ${params.StackName} stack… (may take 5 or 6 minutes to complete)`
  )
  const stack = await cf.send(new CreateStackCommand(params))
  const stackCreation = await waitUntilStackCreateComplete(
    { client: cf },
    { StackName: params.StackName }
  )
  const stackDetails = await cf.send(
    new DescribeStacksCommand({ StackName: params.StackName })
  )

  return stackDetails.Stacks[0]
}
// arn:aws:sns:us-east-1:714022322010:ExampleTopic
export async function getSNSTopicDetails (topicName) {
  const params = {
    TopicArn: getTopicArn(topicName)
  }
  return sns.send(new GetTopicAttributesCommand(params))
}

export async function getSNSTopicSubscriptions (topicName) {
  const params = { TopicArn: getTopicArn(topicName) }

  return sns.send(new ListSubscriptionsByTopicCommand(params))
}

export async function createSNSTopic (topicName) {
  const params = {
    Name: topicName
  }
  const data = await sns.send(new CreateTopicCommand(params))

  return data
}

export async function deleteSNSTopic (topicName) {
  const topicArn = getTopicArn(topicName)
  const params = {
    TopicArn: topicArn
  }
  return sns.send(new DeleteTopicCommand(params))
}

export async function getSNSTopics (nextToken) {
  const params = nextToken ? { NextToken: nextToken } : {}

  const data = await sns.send(new ListTopicsCommand(params))

  if (data?.NextToken) {
    const nextData = await getSNSTopics(data.nextToken)

    return [data.Topics, nextData.Topics].flat()
  }

  return data.Topics
}

export async function publishSNSTopicEvent (topicName, event) {
  const topicArn = getTopicArn(topicName)
  const params = {
    TopicArn: topicArn,
    Message: event
  }
  const data = await sns.send(new PublishCommand(params))

  return data
}

export async function createSubscriptionStack (topicName) {
  const topicArn = getTopicArn(topicName)
  const _topicName = getTopicName(topicName)
  const stackName = `${_topicName}-queue-${config.get('username')}`
  const isStackCreated = await stackExists(stackName)

  if (!isStackCreated) {
    const templatePath = path.resolve(
      __dirname,
      './templates/sns-sqs-eventbridge-cw.yaml'
    )
    const templateBody = readFileSync(templatePath, 'utf8')
    return createStack({
      StackName: stackName,
      TemplateBody: templateBody,
      Parameters: [
        { ParameterKey: 'SNSTopicArn', ParameterValue: topicArn },
        {
          ParameterKey: 'LogGroupName',
          ParameterValue: `/devs/${config.get('username')}/${stackName}`
        },
        {
          ParameterKey: 'StreamName',
          ParameterValue: `${stackName}`
        }
      ],
      Capabilities: ['CAPABILITY_IAM', 'CAPABILITY_AUTO_EXPAND']
    })
  } else {
    return getStackDetails(stackName)
  }
}

export async function watchSubscriptionLogs (logGroupName, streamName) {
  tailLogGroup(logGroupName, streamName)
}

export function getConfig () {
  return config
}
