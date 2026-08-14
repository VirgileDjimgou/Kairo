import '../../../core/api/kairo_api_client.dart';

class ChatCitation {
  const ChatCitation({
    required this.documentTitle,
    required this.excerpt,
    required this.score,
  });
  factory ChatCitation.fromJson(Map<String, dynamic> json) => ChatCitation(
    documentTitle: json['document_title'] as String? ?? '',
    excerpt: json['excerpt'] as String? ?? '',
    score: (json['score'] as num? ?? 0).toDouble(),
  );
  final String documentTitle, excerpt;
  final double score;
}

class ChatReply {
  const ChatReply({
    required this.answer,
    required this.conversationId,
    required this.citations,
    required this.confidence,
    required this.refused,
    this.refusalReason,
  });
  factory ChatReply.fromJson(Map<String, dynamic> json) => ChatReply(
    answer: json['answer'] as String? ?? '',
    conversationId: json['conversation_id'] as String?,
    citations: (json['citations'] as List<dynamic>? ?? <dynamic>[])
        .cast<Map<String, dynamic>>()
        .map(ChatCitation.fromJson)
        .toList(),
    confidence: (json['confidence'] as num? ?? 0).toDouble(),
    refused: json['refused'] as bool? ?? false,
    refusalReason: json['refusal_reason'] as String?,
  );
  final String answer;
  final String? conversationId, refusalReason;
  final List<ChatCitation> citations;
  final double confidence;
  final bool refused;
}

class ChatConversation {
  const ChatConversation({
    required this.id,
    required this.title,
    required this.messageCount,
  });
  factory ChatConversation.fromJson(Map<String, dynamic> json) =>
      ChatConversation(
        id: json['id'] as String,
        title: json['title'] as String? ?? '',
        messageCount: json['message_count'] as int? ?? 0,
      );
  final String id, title;
  final int messageCount;
}

class ChatMessage {
  const ChatMessage({
    required this.role,
    required this.content,
    required this.citations,
  });
  factory ChatMessage.fromJson(Map<String, dynamic> json) => ChatMessage(
    role: json['role'] as String? ?? 'assistant',
    content: json['content'] as String? ?? '',
    citations: (json['citations_json'] as List<dynamic>? ?? <dynamic>[])
        .cast<Map<String, dynamic>>()
        .map(ChatCitation.fromJson)
        .toList(),
  );
  final String role, content;
  final List<ChatCitation> citations;
}

class ChatConversationDetail {
  const ChatConversationDetail({
    required this.id,
    required this.title,
    required this.messages,
  });
  factory ChatConversationDetail.fromJson(Map<String, dynamic> json) =>
      ChatConversationDetail(
        id: json['id'] as String,
        title: json['title'] as String? ?? '',
        messages: (json['messages'] as List<dynamic>? ?? <dynamic>[])
            .cast<Map<String, dynamic>>()
            .map(ChatMessage.fromJson)
            .toList(),
      );
  final String id, title;
  final List<ChatMessage> messages;
}

abstract class ChatGateway {
  Future<List<String>> domainPolicy();
  Future<List<ChatConversation>> conversations();
  Future<ChatConversation> createConversation(String title);
  Future<ChatConversationDetail> conversation(String id);
  Future<ChatReply> query({
    required String question,
    required String locale,
    String? conversationId,
  });
  Stream<Map<String, dynamic>> queryStream({
    required String question,
    required String locale,
    String? conversationId,
  });
}

class HttpChatGateway implements ChatGateway {
  const HttpChatGateway(this._client);
  final KairoApiClient _client;
  @override
  Future<List<String>> domainPolicy() async =>
      ((await _client.getJson('chat/domain-policy'))['allowed_domains']
                  as List<dynamic>? ??
              <dynamic>[])
          .cast<String>();
  @override
  Future<List<ChatConversation>> conversations() async {
    final Object? result = await _client.requestJson(
      'GET',
      'chat/conversations',
    );
    return (result as List<dynamic>)
        .cast<Map<String, dynamic>>()
        .map(ChatConversation.fromJson)
        .toList();
  }

  @override
  Future<ChatConversation> createConversation(String title) async =>
      ChatConversation.fromJson(
        await _client.requestJson(
              'POST',
              'chat/conversations',
              body: <String, dynamic>{'title': title},
            )
            as Map<String, dynamic>,
      );
  @override
  Future<ChatConversationDetail> conversation(String id) async =>
      ChatConversationDetail.fromJson(
        await _client.getJson('chat/conversations/$id'),
      );
  Map<String, dynamic> _payload(String question, String locale, String? id) {
    final payload = <String, dynamic>{
      'question': question,
      'response_language': locale,
    };
    if (id != null) payload['conversation_id'] = id;
    return payload;
  }

  @override
  Future<ChatReply> query({
    required String question,
    required String locale,
    String? conversationId,
  }) async => ChatReply.fromJson(
    await _client.requestJson(
          'POST',
          'chat/query',
          body: _payload(question, locale, conversationId),
        )
        as Map<String, dynamic>,
  );
  @override
  Stream<Map<String, dynamic>> queryStream({
    required String question,
    required String locale,
    String? conversationId,
  }) => _client.requestSse(
    'chat/query-stream',
    body: _payload(question, locale, conversationId),
  );
}
