import { getSNSTopicDetails, getSNSTopicSubscriptions } from '../utils.mjs'

async function viewTopic (topicName) {
  
  const data = await Promise.all([
    getSNSTopicDetails(topicName),
    getSNSTopicSubscriptions(topicName)
  ])
  
  console.log("Details:")
  console.log(data[0].Attributes)
  console.log("")
  console.log("Subscriptions:")
  console.log(data[1].Subscriptions)
}

export default viewTopic
