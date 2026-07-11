# Kafka Notes

Kafka is a distributed event streaming platform. I usually think of it as a
durable log where producers write events and consumers read those events at
their own pace.

Useful ideas:

- A topic is a named stream of events.
- A producer writes messages to a topic.
- A consumer reads messages from a topic.
- Consumer groups let multiple workers share the work.

Question to revisit: how does Kafka retention differ from a regular queue?
