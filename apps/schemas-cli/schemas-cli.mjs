#!/usr/bin/env node

process.env['SUPPRESS_NO_CONFIG_WARNING'] = true

import { Command } from 'commander'

import createSchema from './commands/createSchema.mjs'

const PROGRAM_VERSION = '1.0.0'

const program = new Command()

program.version(PROGRAM_VERSION).description('Description of the app')

program
  .command('create')
  .description('Create a schema')
  .option('--source <string>', 'Source to use for the schema rules')
  .action(createSchema)

program.parse(process.argv)
