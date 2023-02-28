import inquirer from 'inquirer';
import { sns, getTopicArn } from '../utils.mjs';

async function updateTopic(currentTopicArn) {
  const topicName = currentTopicArn.split(':').pop();

  const displayName = await inquirer.prompt([
    {
      type: 'input',
      name: 'displayName',
      message: `Enter a new display name for the SNS topic "${topicName}" (leave blank to keep the current value):`
    }
  ]).then((answers) => answers.displayName);

  const policy = await inquirer.prompt([
    {
      type: 'editor',
      name: 'policy',
      message: `Enter a new policy for the SNS topic "${topicName}" (leave blank to keep the current value):`
    }
  ]).then((answers) => answers.policy.trim());

  const params = {
    TopicArn: currentTopicArn,
    AttributeName: [],
    AttributeValue: []
  };

  if (displayName) {
    params.AttributeName.push('DisplayName');
    params.AttributeValue.push(displayName);
  }

  if (policy) {
    params.AttributeName.push('Policy');
    params.AttributeValue.push(policy);
  }

  if (params.AttributeName.length === 0) {
    console.log('Nothing to update');
    return;
  }

  sns.setTopicAttributes(params, function(err, data) {
    if (err) {
      console.log(err, err.stack);
    } else {
      console.log(`SNS topic "${topicName}" updated`);
    }
  });
}

export default updateTopic;
