import Joi from 'joi'
import fetch from 'node-fetch'
import fs from 'fs/promises'
import parse from 'joi-to-json'

/**
 * Converts a JSON Schema to a Joi schema configuration that can be used by Joi.compile()
 *
 * @param {string} input - URL to a valid JSON Schema
 * @param {string} [outputPath] - Filepath where the converted Joi schema should be saved
 * @returns {Object} converted Joi schema
 */
async function jsonSchemaToJoiSchema (input, outputPath = null) {
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

    const isRequired = key => requiredProperties.includes(key)

    if (schema.type === 'object') {
      let joiSchema = Joi.object()
      if (schema.properties) {
        const keys = {}
        for (const key in schema.properties) {
          keys[key] = convert(schema.properties[key], schema.required)
          if (isRequired(key)) {
            keys[key] = keys[key].required()
          }
        }
        joiSchema = joiSchema.keys(keys)
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

  const joiSchema = convert(resolvedSchema)

  if (outputPath) {
    try {
      await fs.writeFile(
        outputPath,
        JSON.stringify(joiSchema.describe(), null, 2)
      )
      console.log(`Schema saved to: ${outputPath}`)
    } catch (error) {
      throw new Error(`Error writing Joi schema to file: ${error.message}`)
    }
  }

  return joiSchema
}

/**
 * Converts Joi schema configuration (Joi.describe) to a JSON Schema
 *
 * @param {string} input - URL to a valid JSON Schema
 * @param {string} [outputPath] - Filepath where the converted Joi schema should be saved
 * @param {('json'|'open-api'|'json-draft-04'|'json-draft-2019-09')} [version] - Version of JSON Schema to use
 * @returns {Object} converted JSON Schema
 */
async function joiSchemaToJsonSchema (input, outputPath = null, version = 'json') {
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

  const isUrl = typeof input === 'string' && input.startsWith('http')
  const joiSchemaConfig = isUrl ? await fetchSchema(input) : input
  const joiSchema = Joi.compile(joiSchemaConfig)
  const jsonSchema = parse(joiSchema, version)

  if (outputPath) {
    try {
      await fs.writeFile(outputPath, JSON.stringify(jsonSchema, null, 2))
      console.log(`Schema saved to: ${outputPath}`)
    } catch (error) {
      throw new Error(`Error writing Joi schema to file: ${error.message}`)
    }
  }

  return jsonSchema
}

async function convertSchema ({ output, outputType = 'json', source, sourceType = 'joi' }) {
  try {
    const type = `${sourceType}-to-${outputType}`
    console.log(`Attempting ${type} conversion`)
    switch (type) {
      case 'json-to-joi':
        const joiSchema = await jsonSchemaToJoiSchema(source, output)
        break
      case 'joi-to-json':
        const jsonSchema = await joiSchemaToJsonSchema(
          source,
          output,
          outputType
        )
        break
      case 'joi-to-json-draft-04':
        const jsonDraft04Schema = await joiSchemaToJsonSchema(
          source,
          output,
          outputType
        )
        break
      case 'joi-to-json-draft-2019-09':
        const jsonDraft2019Schema = await joiSchemaToJsonSchema(
          source,
          output,
          outputType
        )
        break
      case 'joi-to-open-api':
        const openApiSchema = await joiSchemaToJsonSchema(
          source,
          output,
          outputType
        )
        break
      default:
        throw new Error(`Unknown conversion type (${type})`)
    }
  } catch (error) {
    console.error(`Error: ${error.message}`)
  }
}

export default convertSchema
