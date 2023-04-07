#!/usr/bin/env node

process.env['SUPPRESS_NO_CONFIG_WARNING'] = true

import { Command, Option } from 'commander'

import convertSchema from './commands/convertSchema.mjs'

const PROGRAM_VERSION = '1.0.0'

const program = new Command()

program.version(PROGRAM_VERSION).description('Description of the app')

program
  .command('convert')
  .description('Convert a schema')
  .option('--source <string>', 'Source to use for the schema rules')
  .option('--output <string>', 'Location to save output')
  .addOption(
    new Option('-st, --source-type <string>', 'Type of source')
      .choices(['joi', 'json', 'json-draft-04', 'json-draft-2019-09', 'open-api'])
      .default('json')
  )
  .addOption(
    new Option('-ot, --output-type <string>', 'Type of output')
      .choices(['joi', 'json', 'json-draft-04', 'json-draft-2019-09', 'open-api'])
      .default('joi')
  )
  .action(convertSchema)


program.parse(process.argv)
