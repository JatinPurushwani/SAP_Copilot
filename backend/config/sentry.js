const Sentry = require("@sentry/node");

const initSentry = (app) => {
  if (!process.env.SENTRY_DSN) {
    console.log("Sentry DSN not configured - error tracking disabled");
    return;
  }

  Sentry.init({
    dsn: process.env.SENTRY_DSN,
    environment: process.env.NODE_ENV || "development",

    // Performance Monitoring
    tracesSampleRate:
      process.env.NODE_ENV === "production" ? 0.1 : 1.0,

    // Release tracking
    release: process.env.npm_package_version,

    // Remove sensitive data
    beforeSend(event) {
      if (event.request?.headers) {
        delete event.request.headers.authorization;
        delete event.request.headers.cookie;
      }

      return event;
    },
  });

  console.log("✅ Sentry initialized for error tracking");
};

// Dummy middleware for compatibility
const sentryRequestHandler = () => {
  return (req, res, next) => next();
};

const sentryTracingHandler = () => {
  return (req, res, next) => next();
};

const sentryErrorHandler = () => {
  return (err, req, res, next) => {
    Sentry.captureException(err);
    next(err);
  };
};

module.exports = {
  initSentry,
  sentryRequestHandler,
  sentryTracingHandler,
  sentryErrorHandler,
  Sentry,
};