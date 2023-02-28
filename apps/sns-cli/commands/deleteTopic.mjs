import { deleteSNSTopic } from '../utils.mjs';

async function deleteTopic(topicName) {
  try {
    const data = await deleteSNSTopic(topicName)

    console.log(`deleted ${topicName}`);
  } catch (err) {
    console.log("Error", err.stack);
  }
}

export default deleteTopic;
