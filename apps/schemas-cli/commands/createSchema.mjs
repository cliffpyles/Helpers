import Joi from 'joi'
import fetch from 'node-fetch'

async function jsonSchemaToJoi (input) {
  async function fetchSchema (url) {
    try {
      const response = await fetch(url)
      if (!response.ok) {
        throw new Error(`Failed to fetch JSON schema: ${response.statusText}`)
      }
      return await response.json()
    } catch (error) {
      throw new Error(`Error fetching JSON schema: ${error.message}`)
    }
  }

  function resolveRef (schema, definitions) {
    if (typeof schema === 'object' && schema !== null) {
      if (schema.$ref) {
        const refParts = schema.$ref.split('/')
        console.log(refParts)
        if (refParts[0] === '#') {
          refParts.shift()
        }
        if (refParts[0] === 'definitions') {
          refParts.shift()
          const refKey = refParts.join('/')
          if (definitions.hasOwnProperty(refKey)) {
            return definitions[refKey]
          }
        }
        throw new Error(`Invalid reference: ${schema.$ref}`)
      }

      for (const key in schema) {
        schema[key] = resolveRef(schema[key], definitions)
      }
    }
    return schema
  }

  function convert (schema, requiredProperties = []) {
    if (typeof schema !== 'object' || schema === null) {
      throw new Error('Invalid JSON schema')
    }

    const isRequired = (key) => requiredProperties.includes(key);

    if (schema.type === 'object') {
      let joiSchema = Joi.object()
      if (schema.properties) {
        const keys = {};
        for (const key in schema.properties) {
          keys[key] = convert(schema.properties[key], schema.required);
          if (isRequired(key)) {
            keys[key] = keys[key].required();
          }
        }
        joiSchema = joiSchema.keys(keys);
      }
      return joiSchema
    }

    if (schema.type === 'array') {
      let joiSchema = Joi.array()
      if (schema.items) {
        joiSchema = joiSchema.items(convert(schema.items))
      }
      return joiSchema
    }

    if (schema.type === 'string') {
      let joiSchema = Joi.string()
      if (schema.minLength) {
        joiSchema = joiSchema.min(schema.minLength)
      }
      if (schema.maxLength) {
        joiSchema = joiSchema.max(schema.maxLength)
      }
      if (schema.pattern) {
        joiSchema = joiSchema.pattern(new RegExp(schema.pattern))
      }
      return joiSchema
    }

    if (schema.type === 'number' || schema.type === 'integer') {
      let joiSchema =
        schema.type === 'integer' ? Joi.number().integer() : Joi.number()
      if (schema.minimum !== undefined) {
        joiSchema = joiSchema.min(schema.minimum)
      }
      if (schema.maximum !== undefined) {
        joiSchema = joiSchema.max(schema.maximum)
      }
      return joiSchema
    }

    if (schema.type === 'boolean') {
      return Joi.boolean()
    }

    if (schema.type === 'null') {
      return Joi.valid(null)
    }

    throw new Error(`Unsupported JSON schema type: ${schema.type}`)
  }

  const isUrl = typeof input === 'string' && input.startsWith('http')
  const jsonSchema = isUrl ? await fetchSchema(input) : input

  const definitions = jsonSchema.definitions || {}
  const resolvedSchema = resolveRef(jsonSchema, definitions)

  return convert(resolvedSchema)
}

async function createSchema ({ source }) {
  try {
    const location = new URL(source)

    if (!location?.href?.length) {
      throw new Error('The --source argument must be a valid URL.')
    }

    const joiSchema = await jsonSchemaToJoi(source)

    console.log(joiSchema)

  } catch (error) {
    // console.error('createSchema: ', err)
    console.error(`Error: ${error.message}`);
  }
}

export default createSchema
