import os
import sys
from loguru import logger
from agents.tracing import TracingProcessor, Span, Trace
from agents.tracing.create import (
    AgentSpanData,
    FunctionSpanData,
    GenerationSpanData,
    GuardrailSpanData,
    HandoffSpanData,
)

# Configure Loguru logger
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    ),
    colorize=True,
    backtrace=True,
    diagnose=True,
)

# Custom colors for different log levels
logger.level("INFO", color="<white>")
logger.level("DEBUG", color="<blue>")
logger.level("SUCCESS", color="<green>")
logger.level("WARNING", color="<yellow>")
logger.level("ERROR", color="<red>")
logger.level("CRITICAL", color="<red><bold>")

class CustomLoguruProcessor(TracingProcessor):
    def on_span_start(self, span: Span):
        pass

    def on_span_end(self, span: Span):
        # Check for errors on the span first
        if span.error:
            span_name = getattr(span.span_data, 'name', type(span.span_data).__name__)
            logger.log(
                "ERROR",
                f"ERROR in span '{span_name}' ({span.span_id}): {span.error}"
            )
            # Optionally, you can return here if you don't want to log the regular span info on error
            return

        span_data = span.span_data
        log_message = ""
        log_level = "INFO"
        
        if isinstance(span_data, AgentSpanData):
            log_level = "INFO"
            log_message = f"AGENT: {span_data.name}"
            logger.log(log_level, log_message)

        elif isinstance(span_data, GenerationSpanData):
            log_level = "DEBUG"
            log_message = (
                f"GENERATION: Model '{span_data.model}' - "
                f"Input: {span_data.input}"
            )
            if span_data.output:
                log_message += f" | Output: {span_data.output}"
            logger.log(log_level, log_message)

        elif isinstance(span_data, FunctionSpanData):
            log_level = "INFO"
            log_message = (
                f"TOOL CALL: {span_data.name} - "
                f"Arguments: {span_data.input}"
            )
            if span_data.output:
                log_message += f" | Output: {span_data.output}"
            logger.log(log_level, log_message)

        elif isinstance(span_data, HandoffSpanData):
            log_level = "INFO"
            log_message = (
                f"HANDOFF: From '{span_data.from_agent}' "
                f"to '{span_data.to_agent}'"
            )
            logger.log(log_level, log_message)

        elif isinstance(span_data, GuardrailSpanData):
            log_level = "WARNING"
            log_message = (
                f"GUARDRAIL: {span_data.name} - "
                f"Triggered: {span_data.triggered}"
            )
            logger.log(log_level, log_message)

        else:
            # Log other span types if necessary, or ignore
            log_level = "DEBUG"
            span_name = getattr(span_data, 'name', type(span_data).__name__)
            log_message = f"SPAN ENDED: {span_name} ({span.span_id}) - Type: {type(span_data).__name__}"
            logger.log(log_level, log_message)

    def on_trace_start(self, trace: Trace):
        pass

    def on_trace_end(self, trace: Trace):
        pass

    def force_flush(self):
        pass

    def shutdown(self):
        pass

# Export the logger instance for use in other modules
log = logger
