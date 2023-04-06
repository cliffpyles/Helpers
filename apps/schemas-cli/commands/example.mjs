async function example(exampleArg) {
  try {
    console.log(`Executed example command with ${exampleArg}`);
  } catch (err) {
    console.log("Error", err.stack);
  }
}

export default example;