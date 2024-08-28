#[path = ""]
pub mod events {
    #[path = "sentry_protos.kafka.events.v1.rs"]
    pub mod v1;
}

#[path = ""]
pub mod options {
    #[path = "sentry_protos.options.v1.rs"]
    pub mod v1;
}

#[path = ""]
pub mod relay {
    #[path = "sentry_protos.relay.v1.rs"]
    pub mod v1;
}

#[path = ""]
pub mod snuba {
    #[path = "sentry_protos.snuba.v1alpha.rs"]
    pub mod v1alpha;
}

