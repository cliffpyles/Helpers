import { getConfig } from '../utils.mjs';

const config = getConfig()

function showAll(config) {
    Object.entries(config.store).forEach(([key, value])=> {
        console.log(`${key}: ${value}`)
    })

    return
}


function showKey(key) {
    const value= config.get(key, '(not found)')

    console.log(`${key}: ${value}`)

    return 
}

function setKeyValue(key, value) {
    config.set(key, value)

    console.log(`${key}: ${value}`)

    return
}


async function configure(key, value, ...args) {
    if (!key) {
        return showAll(config)
    }

    if (!value) {
        return showKey(key)
    }

    if (config.has(key)) {
        return setKeyValue(key, value)   
    }

    console.log(`${key} is not a valid key`)
}

export default configure