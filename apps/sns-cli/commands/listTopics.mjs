import { getSNSTopics } from '../utils.mjs'

function sortTopics (topics) {
  return topics.sort((a, b) => {
    const nameA = a.TopicArn.toUpperCase()
    const nameB = b.TopicArn.toUpperCase()

    if (nameA < nameB) {
      return -1
    }

    if (nameA > nameB) {
      return 1
    }

    return 0
  })
}

async function listTopics () {
  try {
    const topics = await getSNSTopics()
    const sortedTopics = sortTopics(topics)

    sortedTopics.forEach(topic => {
      const topicSegments = topic.TopicArn.split(':')

      console.log(`Name: ${topicSegments.at(-1)}`)
      console.log(`ARN: ${topic.TopicArn}`)
      console.log('')
    })
  } catch (err) {
    console.log('Error', err.stack)
  }
}

export default listTopics
