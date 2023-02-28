#!/usr/bin/env node

process.env['SUPPRESS_NO_CONFIG_WARNING'] = true

import { Command } from 'commander';

import createTopic from './commands/createTopic.mjs';
import updateTopic from './commands/updateTopic.mjs';
import deleteTopic from './commands/deleteTopic.mjs';
import viewTopic from './commands/viewTopic.mjs';
import listTopics from './commands/listTopics.mjs';
import subscribeTopic from './commands/subscribeTopic.mjs';
import publishEvent from './commands/publishEvent.mjs';
import configure from './commands/configure.mjs';

const program = new Command();

program
  .version('1.0.0')
  .description('CLI for managing SNS topics');

program
  .command('create')
  .description('Create an SNS topic')
  .argument('[topicName]', 'name of the topic')
  .action(createTopic);

program
  .command('update')
  .description('Update an SNS topic')
  .argument('[topicName]', 'name of the topic')
  .action(updateTopic);

program
  .command('delete')
  .description('Delete an SNS topic')
  .argument('[topicName]', 'name of the topic')
  .action(deleteTopic);

program
  .command('view')
  .description('View details about an SNS topic')
  .argument('[topicName]', 'name of the topic')
  .action(viewTopic);

program
  .command('list')
  .description('List all SNS topics')
  .action(listTopics);

program
  .command('subscribe')
  .description('Subscribe to an SNS topic')
  .argument('[topicName]', 'name of the topic')
  .action(subscribeTopic);

program
  .command('publish')
  .description('Publish an event to a topic')
  .argument('[topicName]', 'name of the topic')
  .action(publishEvent);

program
  .command('config')
  .description('Manage settings for sns-cli')
  .argument('[key]', 'key for the sns-cli setting')
  .argument('[value]', 'new value for the sns-cli setting')
  .action(configure);

program.parse(process.argv);
