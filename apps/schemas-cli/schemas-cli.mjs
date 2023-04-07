#!/usr/bin/env node

process.env['SUPPRESS_NO_CONFIG_WARNING'] = true

import { Command } from 'commander'

import convertSchema from './commands/convertSchema.mjs'

const PROGRAM_VERSION = '1.0.0'

const program = new Command()

program.version(PROGRAM_VERSION).description('Description of the app')

program
  .command('convert')
  .description('Convert a schema')
  .option('--source <string>', 'Source to use for the schema rules')
  .option('--output <string>', 'Location to save output')
  .action(convertSchema)

program.parse(process.argv)
