import { createSNSTopic } from '../utils.mjs';

async function createTopic(topicName) {
  try {
    const data = await createSNSTopic(topicName)
    console.log(`${topicName} created (${data.TopicArn})`);
  } catch (err) {
    console.log("Error", err.stack);
  }
}

export default createTopic;
