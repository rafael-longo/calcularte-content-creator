## Responses

OpenAI's most advanced interface for generating model responses. Supports text and image inputs, and text outputs. Create stateful interactions with the model, using the output of previous responses as input. Extend the model's capabilities with built-in tools for file search, web search, computer use, and more. Allow the model access to external systems and data using function calling.

Related guides:

* [Quickstart](/docs/quickstart?api-mode=responses)
* [Text inputs and outputs](/docs/guides/text?api-mode=responses)
* [Image inputs](/docs/guides/images?api-mode=responses)
* [Structured Outputs](/docs/guides/structured-outputs?api-mode=responses)
* [Function calling](/docs/guides/function-calling?api-mode=responses)
* [Conversation state](/docs/guides/conversation-state?api-mode=responses)
* [Extend the models with tools](/docs/guides/tools?api-mode=responses)

---

## Create a model response

**POST** `https://api.openai.com/v1/responses`

Creates a model response. Provide [text](/docs/guides/text) or [image](/docs/guides/images) inputs to generate [text](/docs/guides/text) or [JSON](/docs/guides/structured-outputs) outputs. Have the model call your own [custom code](/docs/guides/function-calling) or use built-in [tools](/docs/guides/tools) like [web search](/docs/guides/tools-web-search) or [file search](/docs/guides/tools-file-search) to use your own data as input for the model's response.

### Request body

* `background`: boolean or null (Optional, Defaults to false)
    Whether to run the model response in the background. [Learn more](/docs/guides/background).
* `include`: array or null (Optional)
    Specify additional output data to include in the model response. Currently supported values are:
    * `code_interpreter_call.outputs`: Includes the outputs of python code execution in code interpreter tool call items.
    * `computer_call_output.output.image_url`: Include image urls from the computer call output.
    * `file_search_call.results`: Include the search results of the file search tool call.
    * `message.input_image.image_url`: Include image urls from the input message.
    * `message.output_text.logprobs`: Include logprobs with assistant messages.
    * `reasoning.encrypted_content`: Includes an encrypted version of reasoning tokens in reasoning item outputs. This enables reasoning items to be used in multi-turn conversations when using the Responses API statelessly (like when the `store` parameter is set to `false`, or when an organization is enrolled in the zero data retention program).
* `input`: string or array (Optional)
    Text, image, or file inputs to the model, used to generate a response.

    Learn more:
    * [Text inputs and outputs](/docs/guides/text)
    * [Image inputs](/docs/guides/images)
    * [File inputs](/docs/guides/pdf-files)
    * [Conversation state](/docs/guides/conversation-state)
    * [Function calling](/docs/guides/function-calling)
* `instructions`: string or null (Optional)
    A system (or developer) message inserted into the model's context.

    When using along with `previous_response_id`, the instructions from a previous response will not be carried over to the next response. This makes it simple to swap out system (or developer) messages in new responses.
* `max_output_tokens`: integer or null (Optional)
    An upper bound for the number of tokens that can be generated for a response, including visible output tokens and [reasoning tokens](/docs/guides/reasoning).
* `max_tool_calls`: integer or null (Optional)
    The maximum number of total calls to built-in tools that can be processed in a response. This maximum number applies across all built-in tool calls, not per individual tool. Any further attempts to call a tool by the model will be ignored.
* `metadata`: map (Optional)
    Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard.

    Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.
* `model`: string (Optional)
    Model ID used to generate the response, like `gpt-4o` or `o3`. OpenAI offers a wide range of models with different capabilities, performance characteristics, and price points. Refer to the [model guide](/docs/models) to browse and compare available models.
* `parallel_tool_calls`: boolean or null (Optional, Defaults to true)
    Whether to allow the model to run tool calls in parallel.
* `previous_response_id`: string or null (Optional)
    The unique ID of the previous response to the model. Use this to create multi-turn conversations. Learn more about [conversation state](/docs/guides/conversation-state).
* `prompt`: object or null (Optional)
    Reference to a prompt template and its variables. [Learn more](/docs/guides/text?api-mode=responses#reusable-prompts).
* `reasoning`: object or null (Optional)
    **o-series models only**

    Configuration options for [reasoning models](https://platform.openai.com/docs/guides/reasoning).
* `service_tier`: string or null (Optional, Defaults to auto)
    Specifies the processing type used for serving the request.
    * If set to 'auto', then the request will be processed with the service tier configured in the Project settings. Unless otherwise configured, the Project will use 'default'.
    * If set to 'default', then the request will be processed with the standard pricing and performance for the selected model.
    * If set to '[flex](/docs/guides/flex-processing)' or 'priority', then the request will be processed with the corresponding service tier. [Contact sales](https://openai.com/contact-sales) to learn more about Priority processing.
    * When not set, the default behavior is 'auto'.

    When the `service_tier` parameter is set, the response body will include the `service_tier` value based on the processing mode actually used to serve the request. This response value may be different from the value set in the parameter.
* `store`: boolean or null (Optional, Defaults to true)
    Whether to store the generated model response for later retrieval via API.
* `stream`: boolean or null (Optional, Defaults to false)
    If set to true, the model response data will be streamed to the client as it is generated using [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format). See the [Streaming section below](/docs/api-reference/responses-streaming) for more information.
* `temperature`: number or null (Optional, Defaults to 1)
    What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. We generally recommend altering this or `top_p` but not both.
* `text`: object (Optional)
    Configuration options for a text response from the model. Can be plain text or structured JSON data. Learn more:
    * [Text inputs and outputs](/docs/guides/text)
    * [Structured Outputs](/docs/guides/structured-outputs)
* `tool_choice`: string or object (Optional)
    How the model should select which tool (or tools) to use when generating a response. See the `tools` parameter to see how to specify which tools the model can call.
* `tools`: array (Optional)
    An array of tools the model may call while generating a response. You can specify which tool to use by setting the `tool_choice` parameter.

    The two categories of tools you can provide the model are:
    * **Built-in tools**: Tools that are provided by OpenAI that extend the model's capabilities, like [web search](/docs/guides/tools-web-search) or [file search](/docs/guides/tools-file-search). Learn more about [built-in tools](/docs/guides/tools).
    * **Function calls (custom tools)**: Functions that are defined by you, enabling the model to call your own code. Learn more about [function calling](/docs/guides/function-calling).
* `top_logprobs`: integer or null (Optional)
    An integer between 0 and 20 specifying the number of most likely tokens to return at each token position, each with an associated log probability.
* `top_p`: number or null (Optional, Defaults to 1)
    An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.

    We generally recommend altering this or `temperature` but not both.
* `truncation`: string or null (Optional, Defaults to disabled)
    The truncation strategy to use for the model response.
    * `auto`: If the context of this response and previous ones exceeds the model's context window size, the model will truncate the response to fit the context window by dropping input items in the middle of the conversation.
    * `disabled` (default): If a model response will exceed the context window size for a model, the request will fail with a 400 error.
* `user`: string (Optional)
    A stable identifier for your end-users. Used to boost cache hit rates by better bucketing similar requests and to help OpenAI detect and prevent abuse. [Learn more](/docs/guides/safety-best-practices#end-user-ids).

### Returns

Returns a [Response](/docs/api-reference/responses/object) object.

---

## Get a model response

**GET** `https://api.openai.com/v1/responses/{response_id}`

Retrieves a model response with the given ID.

### Path parameters

* `response_id`: string (Required)
    The ID of the response to retrieve.

### Query parameters

* `include`: array (Optional)
    Additional fields to include in the response. See the `include` parameter for Response creation above for more information.
* `starting_after`: integer (Optional)
    The sequence number of the event after which to start streaming.
* `stream`: boolean (Optional)
    If set to true, the model response data will be streamed to the client as it is generated using [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format). See the [Streaming section below](/docs/api-reference/responses-streaming) for more information.

### Returns

The [Response](/docs/api-reference/responses/object) object matching the specified ID.

---

## Delete a model response

**DELETE** `https://api.openai.com/v1/responses/{response_id}`

Deletes a model response with the given ID.

### Path parameters

* `response_id`: string (Required)
    The ID of the response to delete.

### Returns

A success message.

---

## Cancel a response

**POST** `https://api.openai.com/v1/responses/{response_id}/cancel`

Cancels a model response with the given ID. Only responses created with the `background` parameter set to `true` can be cancelled. [Learn more](/docs/guides/background).

### Path parameters

* `response_id`: string (Required)
    The ID of the response to cancel.

### Returns

A [Response](/docs/api-reference/responses/object) object.

---

## The response object

Represents a model response returned by model, based on the provided input.

* `background`: boolean or null
    Whether to run the model response in the background. [Learn more](/docs/guides/background).
* `created_at`: number
    Unix timestamp (in seconds) of when this Response was created.
* `error`: object or null
    An error object returned when the model fails to generate a Response.
* `id`: string
    Unique identifier for this Response.
* `incomplete_details`: object or null
    Details about why the response is incomplete.
* `instructions`: string or array
    A system (or developer) message inserted into the model's context.

    When using along with `previous_response_id`, the instructions from a previous response will not be carried over to the next response. This makes it simple to swap out system (or developer) messages in new responses.
* `max_output_tokens`: integer or null
    An upper bound for the number of tokens that can be generated for a response, including visible output tokens and [reasoning tokens](/docs/guides/reasoning).
* `max_tool_calls`: integer or null
    The maximum number of total calls to built-in tools that can be processed in a response. This maximum number applies across all built-in tool calls, not per individual tool. Any further attempts to call a tool by the model will be ignored.
* `metadata`: map
    Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard.

    Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.
* `model`: string
    Model ID used to generate the response, like `gpt-4o` or `o3`. OpenAI offers a wide range of models with different capabilities, performance characteristics, and price points. Refer to the [model guide](/docs/models) to browse and compare available models.
* `object`: string
    The object type of this resource - always set to `response`.
* `output`: array
    An array of content items generated by the model.
    * The length and order of items in the `output` array is dependent on the model's response.
    * Rather than accessing the first item in the `output` array and assuming it's an `assistant` message with the content generated by the model, you might consider using the `output_text` property where supported in SDKs.
* `output_text`: string or null (SDK Only)
    SDK-only convenience property that contains the aggregated text output from all `output_text` items in the `output` array, if any are present. Supported in the Python and JavaScript SDKs.
* `parallel_tool_calls`: boolean
    Whether to allow the model to run tool calls in parallel.
* `previous_response_id`: string or null
    The unique ID of the previous response to the model. Use this to create multi-turn conversations. Learn more about [conversation state](/docs/guides/conversation-state).
* `prompt`: object or null
    Reference to a prompt template and its variables. [Learn more](/docs/guides/text?api-mode=responses#reusable-prompts).
* `reasoning`: object or null
    **o-series models only**

    Configuration options for [reasoning models](https://platform.openai.com/docs/guides/reasoning).
* `service_tier`: string or null
    Specifies the processing type used for serving the request.
    * If set to 'auto', then the request will be processed with the service tier configured in the Project settings. Unless otherwise configured, the Project will use 'default'.
    * If set to 'default', then the request will be processed with the standard pricing and performance for the selected model.
    * If set to '[flex](/docs/guides/flex-processing)' or 'priority', then the request will be processed with the corresponding service tier. [Contact sales](https://openai.com/contact-sales) to learn more about Priority processing.
    * When not set, the default behavior is 'auto'.

    When the `service_tier` parameter is set, the response body will include the `service_tier` value based on the processing mode actually used to serve the request. This response value may be different from the value set in the parameter.
* `status`: string
    The status of the response generation. One of `completed`, `failed`, `in_progress`, `cancelled`, `queued`, or `incomplete`.
* `temperature`: number or null
    What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. We generally recommend altering this or `top_p` but not both.
* `text`: object
    Configuration options for a text response from the model. Can be plain text or structured JSON data. Learn more:
    * [Text inputs and outputs](/docs/guides/text)
    * [Structured Outputs](/docs/guides/structured-outputs)
* `tool_choice`: string or object
    How the model should select which tool (or tools) to use when generating a response. See the `tools` parameter to see how to specify which tools the model can call.
* `tools`: array
    An array of tools the model may call while generating a response. You can specify which tool to use by setting the `tool_choice` parameter.

    The two categories of tools you can provide the model are:
    * **Built-in tools**: Tools that are provided by OpenAI that extend the model's capabilities, like [web search](/docs/guides/tools-web-search) or [file search](/docs/guides/tools-file-search). Learn more about [built-in tools](/docs/guides/tools).
    * **Function calls (custom tools)**: Functions that are defined by you, enabling the model to call your own code. Learn more about [function calling](/docs/guides/function-calling).
* `top_logprobs`: integer or null
    An integer between 0 and 20 specifying the number of most likely tokens to return at each token position, each with an associated log probability.
* `top_p`: number or null
    An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.

    We generally recommend altering this or `temperature` but not both.
* `truncation`: string or null
    The truncation strategy to use for the model response.
    * `auto`: If the context of this response and previous ones exceeds the model's context window size, the model will truncate the response to fit the context window by dropping input items in the middle of the conversation.
    * `disabled` (default): If a model response will exceed the context window size for a model, the request will fail with a 400 error.
* `usage`: object
    Represents token usage details including input tokens, output tokens, a breakdown of output tokens, and the total tokens used.
* `user`: string
    A stable identifier for your end-users. Used to boost cache hit rates by better bucketing similar requests and to help OpenAI detect and prevent abuse. [Learn more](/docs/guides/safety-best-practices#end-user-ids).

---

## List input items

**GET** `https://api.openai.com/v1/responses/{response_id}/input_items`

Returns a list of input items for a given response.

### Path parameters

* `response_id`: string (Required)
    The ID of the response to retrieve input items for.

### Query parameters

* `after`: string (Optional)
    An item ID to list items after, used in pagination.
* `before`: string (Optional)
    An item ID to list items before, used in pagination.
* `include`: array (Optional)
    Additional fields to include in the response. See the `include` parameter for Response creation above for more information.
* `limit`: integer (Optional, Defaults to 20)
    A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.
* `order`: string (Optional, Defaults to desc)
    The order to return the input items in. Default is `desc`.
    * `asc`: Return the input items in ascending order.
    * `desc`: Return the input items in descending order.

### Returns

A list of input item objects.

---

## The input item list

A list of Response items.

* `data`: array
    A list of items used to generate this response.
* `first_id`: string
    The ID of the first item in the list.
* `has_more`: boolean
    Whether there are more items available.
* `last_id`: string
    The ID of the last item in the list.
* `object`: string
    The type of this object. It is always set to "list".

---

## Streaming

When you [create a Response](/docs/api-reference/responses/create) with `stream` set to `true`, the server will emit server-sent events to the client as the Response is generated. This section contains the events that are emitted by the server.

[Learn more about streaming responses](/docs/guides/streaming-responses?api-mode=responses).

---

## response.created

An event that is emitted when a response is created.

* `response`: object
    The response that was created.
* `sequence_number`: integer
    The sequence number for this event.
* `type`: string
    The type of the event. Always `response.created`.

---

## response.in_progress

Emitted when the response is in progress.

* `response`: object
    The response that is in progress.
* `sequence_number`: integer
    The sequence number of this event.
* `type`: string
    The type of the event. Always `response.in_progress`.

---

## response.completed

Emitted when the model response is complete.

* `response`: object
    Properties of the completed response.
* `sequence_number`: integer
    The sequence number for this event.
* `type`: string
    The type of the event. Always `response.completed`.

---

## response.failed

An event that is emitted when a response fails.

* `response`: object
    The response that failed.
* `sequence_number`: integer
    The sequence number of this event.
* `type`: string
    The type of the event. Always `response.failed`.

---

## response.incomplete

An event that is emitted when a response finishes as incomplete.

* `response`: object
    The response that was incomplete.
* `sequence_number`: integer
    The sequence number of this event.
* `type`: string
    The type of the event. Always `response.incomplete`.

---

## response.output_item.added

Emitted when a new output item is added.

* `item`: object
    The output item that was added.
* `output_index`: integer
    The index of the output item that was added.
* `sequence_number`: integer
    The sequence number of this event.
* `type`: string
    The type of the event. Always `response.output_item.added`.

---

## response.output_item.done

Emitted when an output item is marked done.

* `item`: object
    The output item that was marked done.
* `output_index`: integer
    The index of the output item that was marked done.
* `sequence_number`: integer
    The sequence number of this event.
* `type`: string
    The type of the event. Always `response.output_item.done`.

---

## response.output_text.delta

Emitted when there is an additional text delta.

* `content_index`: integer
    The index of the content part that the text delta was added to.
* `delta`: string
    The text delta that was added.
* `item_id`: string
    The ID of the output item that the text delta was added to.
* `output_index`: integer
    The index of the output item that the text delta was added to.
* `sequence_number`: integer
    The sequence number for this event.
* `type`: string
    The type of the event. Always `response.output_text.delta`.

---

## response.output_text.done

Emitted when text content is finalized.

* `content_index`: integer
    The index of the content part that the text content is finalized.
* `item_id`: string
    The ID of the output item that the text content is finalized.
* `output_index`: integer
    The index of the output item that the text content is finalized.
* `sequence_number`: integer
    The sequence number for this event.
* `text`: string
    The text content that is finalized.
* `type`: string
    The type of the event. Always `response.output_text.done`.

---

## response.refusal.delta

Emitted when there is a partial refusal text.

* `content_index`: integer
    The index of the content part that the refusal text is added to.
* `delta`: string
    The refusal text that is added.
* `item_id`: string
    The ID of the output item that the refusal text is added to.
* `output_index`: integer
    The index of the output item that the refusal text is added to.
* `sequence_number`: integer
    The sequence number of this event.
* `type`: string
    The type of the event. Always `response.refusal.delta`.

---

## response.refusal.done

Emitted when refusal text is finalized.

* `content_index`: integer
    The index of the content part that the refusal text is finalized.
* `item_id`: string
    The ID of the output item that the refusal text is finalized.
* `output_index`: integer
    The index of the output item that the refusal text is finalized.
* `refusal`: string
    The refusal text that is finalized.
* `sequence_number`: integer
    The sequence number of this event.
* `type`: string
    The type of the event. Always `response.refusal.done`.

---

## response.function_call_arguments.delta

Emitted when there is a partial function-call arguments delta.

* `delta`: object
    The partial update to the arguments for the MCP tool call.
* `item_id`: string
    The unique identifier of the MCP tool call item being processed.
* `output_index`: integer
    The index of the output item in the response's output array.
* `sequence_number`: integer
    The sequence number of this event.
* `type`: string
    The type of the event. Always `response.function_call_arguments.delta`.

---

## response.function_call_arguments.done

Emitted when function-call arguments are finalized.

* `arguments`: string
    The function-call arguments.
* `item_id`: string
    The ID of the item.
* `output_index`: integer
    The index of the output item.
* `sequence_number`: integer
    The sequence number of this event.
* `type`: string

---

## response.file_search_call.in_progress

Emitted when a file search call is initiated.

* `item_id`: string
    The ID of the output item that the file search call is initiated.
* `output_index`: integer
    The index of the output item that the file search call is initiated.
* `sequence_number`: integer
    The sequence number of this event.
* `type`: string
    The type of the event. Always `response.file_search_call.in_progress`.

---

## response.file_search_call.searching

Emitted when a file search is currently searching.

* `item_id`: string
    The ID of the output item that the file search call is initiated.
* `output_index`: integer
    The index of the output item that the file search call is searching.
* `sequence_number`: integer
    The sequence number of this event.
* `type`: string
    The type of the event. Always `response.file_search_call.searching`.

---

## response.file_search_call.completed

Emitted when a file search call is completed (results found).

* `item_id`: string
    The ID of the output item that the file search call is initiated.
* `output_index`: integer
    The index of the output item that the file search call is initiated.
* `sequence_number`: integer
    The sequence number of this event.
* `type`: string
    The type of the event. Always `response.file_search_call.completed`.

---

## response.web_search_call.in_progress

Emitted when a web search call is initiated.

* `item_id`: string
    Unique ID for the output item associated with the web search call.
* `output_index`: integer
    The index of the output item that the web search call is associated with.
* `sequence_number`: integer
    The sequence number of the web search call being processed.
* `type`: string
    The type of the event. Always `response.web_search_call.in_progress`.

---

## response.web_search_call.searching

Emitted when a web search call is executing.

* `item_id`: string
    Unique ID for the output item associated with the web search call.
* `output_index`: integer
    The index of the output item that the web search call is associated with.
* `sequence_number`: integer
    The sequence number of the web search call being processed.
* `type`: string
    The type of the event. Always `response.web_search_call.searching`.

---

## response.web_search_call.completed

Emitted when a web search call is completed.

* `item_id`: string
    Unique ID for the output item associated with the web search call.
* `output_index`: integer
    The index of the output item that the web search call is associated with.
* `sequence_number`: integer
    The sequence number of the web search call being processed.
* `type`: string
    The type of the event. Always `response.web_search_call.completed`.

---

## response.reasoning_summary_part.added

Emitted when a new reasoning summary part is added.

* `item_id`: string
    The ID of the item this summary part is associated with.
* `output_index`: integer
    The index of the output item this summary part is associated with.
* `part`: object
    The summary part that was added.
* `sequence_number`: integer
    The sequence number of this event.
* `summary_index`: integer
    The index of the summary part within the reasoning summary.
* `type`: string
    The type of the event. Always `response.reasoning_summary_part.added`.

---

## response.reasoning_summary_part.done

Emitted when a reasoning summary part is completed.

* `item_id`: string
    The ID of the item this summary part is associated with.
* `output_index`: integer
    The index of the output item this summary part is associated with.
* `part`: object
    The completed summary part.
* `sequence_number`: integer
    The sequence number of this event.
* `summary_index`: integer
    The index of the summary part within the reasoning summary.
* `type`: string
    The type of the event. Always `response.reasoning_summary_part.done`.

---

## response.reasoning_summary_text.delta

Emitted when a delta is added to a reasoning summary text.

* `delta`: object
    The text delta that was added to the summary.
* `item_id`: string
    The ID of the item this summary text delta is associated with.
* `output_index`: integer
    The index of the output item this summary text delta is associated with.
* `sequence_number`: integer
    The sequence number of this event.
* `summary_index`: integer
    The index of the summary part within the reasoning summary.
* `type`: string
    The type of the event. Always `response.reasoning_summary_text.delta`.

---

## response.reasoning_summary_text.done

Emitted when a reasoning summary text is completed.

* `item_id`: string
    The ID of the item this summary text is associated with.
* `output_index`: integer
    The index of the output item this summary text is associated with.
* `sequence_number`: integer
    The sequence number of this event.
* `summary_index`: integer
    The index of the summary part within the reasoning summary.
* `text`: string
    The full text of the completed reasoning summary.
* `type`: string
    The type of the event. Always `response.reasoning_summary_text.done`.

---

## response.image_generation_call.completed

Emitted when an image generation tool call has completed and the final image is available.

* `item_id`: string
    The unique identifier of the image generation item being processed.
* `output_index`: integer
    The index of the output item in the response's output array.
* `sequence_number`: integer
    The sequence number of this event.
* `type`: string
    The type of the event. Always 'response.image_generation_call.completed'.

---

## response.image_generation_call.generating

Emitted when an image generation tool call is actively generating an image (intermediate state).

* `item_id`: string
    The unique identifier of the image generation item being processed.
* `output_index`: integer
    The index of the output item in the response's output array.
* `sequence_number`: integer
    The sequence number of the image generation item being processed.
* `type`: string
    The type of the event. Always 'response.image_generation_call.generating'.

---

## response.image_generation_call.in_progress

Emitted when an image generation tool call is in progress.

* `item_id`: string
    The unique identifier of the image generation item being processed.
* `output_index`: integer
    The index of the output item in the response's output array.
* `sequence_number`: integer
    The sequence number of the image generation item being processed.
* `type`: string
    The type of the event. Always 'response.image_generation_call.in_progress'.

---

## response.image_generation_call.partial_image

Emitted when a partial image is available during image generation streaming.

* `item_id`: string
    The unique identifier of the image generation item being processed.
* `output_index`: integer
    The index of the output item in the response's output array.
* `partial_image_b64`: string
    Base64-encoded partial image data, suitable for rendering as an image.
* `partial_image_index`: integer
    0-based index for the partial image (backend is 1-based, but this is 0-based for the user).
* `sequence_number`: integer
    The sequence number of the image generation item being processed.
* `type`: string
    The type of the event. Always 'response.image_generation_call.partial_image'.

---

## response.mcp_call_arguments.delta

Emitted when there is a delta (partial update) to the arguments of an MCP tool call.

* `delta`: object
    The partial update to the arguments for the MCP tool call.
* `item_id`: string
    The unique identifier of the MCP tool call item being processed.
* `output_index`: integer
    The index of the output item in the response's output array.
* `sequence_number`: integer
    The sequence number of this event.
* `type`: string
    The type of the event. Always 'response.mcp_call_arguments.delta'.

---

## response.mcp_call_arguments.done

Emitted when the arguments for an MCP tool call are finalized.

* `arguments`: object
    The finalized arguments for the MCP tool call.
* `item_id`: string
    The unique identifier of the MCP tool call item being processed.
* `output_index`: integer
    The index of the output item in the response's output array.
* `sequence_number`: integer
    The sequence number of this event.
* `type`: string
    The type of the event. Always 'response.mcp_call_arguments.done'.

---

## response.mcp_call.completed

Emitted when an MCP tool call has completed successfully.

* `sequence_number`: integer
    The sequence number of this event.
* `type`: string
    The type of the event. Always 'response.mcp_call.completed'.

---

## response.mcp_call.failed

Emitted when an MCP tool call has failed.

* `sequence_number`: integer
    The sequence number of this event.
* `type`: string
    The type of the event. Always 'response.mcp_call.failed'.

---

## response.mcp_call.in_progress

Emitted when an MCP tool call is in progress.

* `item_id`: string
    The unique identifier of the MCP tool call item being processed.
* `output_index`: integer
    The index of the output item in the response's output array.
* `sequence_number`: integer
    The sequence number of this event.
* `type`: string
    The type of the event. Always 'response.mcp_call.in_progress'.

---

## response.mcp_list_tools.completed

Emitted when the list of available MCP tools has been successfully retrieved.

* `sequence_number`: integer
    The sequence number of this event.
* `type`: string
    The type of the event. Always 'response.mcp_list_tools.completed'.

---

## response.mcp_list_tools.failed

Emitted when the attempt to list available MCP tools has failed.

* `sequence_number`: integer
    The sequence number of this event.
* `type`: string
    The type of the event. Always 'response.mcp_list_tools.failed'.

---

## response.mcp_list_tools.in_progress

Emitted when the system is in the process of retrieving the list of available MCP tools.

* `sequence_number`: integer
    The sequence number of this event.
* `type`: string
    The type of the event. Always 'response.mcp_list_tools.in_progress'.

---

## response.code_interpreter_call.in_progress

Emitted when a code interpreter call is in progress.

* `item_id`: string
    The unique identifier of the code interpreter tool call item.
* `output_index`: integer
    The index of the output item in the response for which the code interpreter call is in progress.
* `sequence_number`: integer
    The sequence number of this event, used to order streaming events.
* `type`: string
    The type of the event. Always `response.code_interpreter_call.in_progress`.

---

## response.code_interpreter_call.interpreting

Emitted when the code interpreter is actively interpreting the code snippet.

* `item_id`: string
    The unique identifier of the code interpreter tool call item.
* `output_index`: integer
    The index of the output item in the response for which the code interpreter is interpreting code.
* `sequence_number`: integer
    The sequence number of this event, used to order streaming events.
* `type`: string
    The type of the event. Always `response.code_interpreter_call.interpreting`.

---

## response.code_interpreter_call.completed

Emitted when the code interpreter call is completed.

* `item_id`: string
    The unique identifier of the code interpreter tool call item.
* `output_index`: integer
    The index of the output item in the response for which the code interpreter call is completed.
* `sequence_number`: integer
    The sequence number of this event, used to order streaming events.
* `type`: string
    The type of the event. Always `response.code_interpreter_call.completed`.

---

## response.code_interpreter_call_code.delta

Emitted when a partial code snippet is streamed by the code interpreter.

* `delta`: string
    The partial code snippet being streamed by the code interpreter.
* `item_id`: string
    The unique identifier of the code interpreter tool call item.
* `output_index`: integer
    The index of the output item in the response for which the code is being streamed.
* `sequence_number`: integer
    The sequence number of this event, used to order streaming events.
* `type`: string
    The type of the event. Always `response.code_interpreter_call_code.delta`.

---

## response.code_interpreter_call_code.done

Emitted when the code snippet is finalized by the code interpreter.

* `code`: string
    The final code snippet output by the code interpreter.
* `item_id`: string
    The unique identifier of the code interpreter tool call item.
* `output_index`: integer
    The index of the output item in the response for which the code is finalized.
* `sequence_number`: integer
    The sequence number of this event, used to order streaming events.
* `type`: string
    The type of the event. Always `response.code_interpreter_call_code.done`.

---

## response.output_text.annotation.added

Emitted when an annotation is added to output text content.

* `annotation`: object
    The annotation object being added. (See annotation schema for details.)
* `annotation_index`: integer
    The index of the annotation within the content part.
* `content_index`: integer
    The index of the content part within the output item.
* `item_id`: string
    The unique identifier of the item to which the annotation is being added.
* `output_index`: integer
    The index of the output item in the response's output array.
* `sequence_number`: integer
    The sequence number of this event.
* `type`: string
    The type of the event. Always `response.output_text.annotation.added`.

---

## response.queued

Emitted when a response is queued and waiting to be processed.

* `response`: object
    The full response object that is queued.
* `sequence_number`: integer
    The sequence number for this event.
* `type`: string
    The type of the event. Always 'response.queued'.

---

## response.reasoning.delta

Emitted when there is a delta (partial update) to the reasoning content.

* `content_index`: integer
    The index of the reasoning content part within the output item.
* `delta`: object
    The partial update to the reasoning content.
* `item_id`: string
    The unique identifier of the item for which reasoning is being updated.
* `output_index`: integer
    The index of the output item in the response's output array.
* `sequence_number`: integer
    The sequence number of this event.
* `type`: string
    The type of the event. Always 'response.reasoning.delta'.

---

## response.reasoning.done

Emitted when the reasoning content is finalized for an item.

* `content_index`: integer
    The index of the reasoning content part within the output item.
* `item_id`: string
    The unique identifier of the item for which reasoning is finalized.
* `output_index`: integer
    The index of the output item in the response's output array.
* `sequence_number`: integer
    The sequence number of this event.
* `text`: string
    The finalized reasoning text.
* `type`: string
    The type of the event. Always 'response.reasoning.done'.

---

## response.reasoning_summary.delta

Emitted when there is a delta (partial update) to the reasoning summary content.

* `delta`: object
    The partial update to the reasoning summary content.
* `item_id`: string
    The unique identifier of the item for which the reasoning summary is being updated.
* `output_index`: integer
    The index of the output item in the response's output array.
* `sequence_number`: integer
    The sequence number of this event.
* `summary_index`: integer
    The index of the summary part within the output item.
* `type`: string
    The type of the event. Always 'response.reasoning_summary.delta'.

---

## response.reasoning_summary.done

Emitted when the reasoning summary content is finalized for an item.

* `item_id`: string
    The unique identifier of the item for which the reasoning summary is finalized.
* `output_index`: integer
    The index of the output item in the response's output array.
* `sequence_number`: integer
    The sequence number of this event.
* `summary_index`: integer
    The index of the summary part within the reasoning summary.
* `text`: string
    The full text of the completed reasoning summary.
* `type`: string
    The type of the event. Always 'response.reasoning_summary.done'.

---

## error

Emitted when an error occurs.

* `code`: string or null
    The error code.
* `message`: string
    The error message.
* `param`: string or null
    The error parameter.
* `sequence_number`: integer
    The sequence number of this event.
* `type`: string
    The type of the event. Always `error`.

---

