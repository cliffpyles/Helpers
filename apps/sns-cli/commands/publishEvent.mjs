import inquirer from 'inquirer';
import { publishSNSTopicEvent } from '../utils.mjs';

async function publishEvent(topicName, ...args) {
  const data = await publishSNSTopicEvent(topicName, "example event occured")
  console.log(data)
}

export default publishEvent;
