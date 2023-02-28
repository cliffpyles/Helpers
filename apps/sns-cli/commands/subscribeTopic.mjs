import { createSubscriptionStack, watchSubscriptionLogs } from '../utils.mjs'






async function subscribeTopic (topicName) {
  const subscriptionStack = await createSubscriptionStack(topicName)
  const stackParams = subscriptionStack.Parameters.reduce((accum, param) => {
    return { ...accum, [param.ParameterKey]: param.ParameterValue }
  }, {})
  
  watchSubscriptionLogs(stackParams.LogGroupName, stackParams.StreamName)
}

export default subscribeTopic
