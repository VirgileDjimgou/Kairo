import 'package:flutter/material.dart';

import '../../../app/localization/kairo_localizations.dart';
import '../../../core/api/kairo_api_client.dart';
import '../data/chat_gateway.dart';

class ChatWorkspacePage extends StatefulWidget {
  const ChatWorkspacePage({
    super.key,
    required this.gateway,
    required this.locale,
  });

  final ChatGateway gateway;
  final KairoLocale locale;

  @override
  State<ChatWorkspacePage> createState() => _ChatWorkspacePageState();
}

class _ChatWorkspacePageState extends State<ChatWorkspacePage> {
  final _questionController = TextEditingController();
  late final _ChatText _text = _ChatText(widget.locale);
  List<ChatConversation> _conversations = const <ChatConversation>[];
  List<ChatMessage> _messages = const <ChatMessage>[];
  List<String> _domains = const <String>[];
  String? _conversationId;
  String? _runtimeState;
  String _streamingAnswer = '';
  bool _loading = true;
  bool _asking = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _questionController.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _runtimeState = null;
    });
    try {
      final results = await Future.wait<Object>(<Future<Object>>[
        widget.gateway.conversations(),
        widget.gateway.domainPolicy(),
      ]);
      if (!mounted) return;
      setState(() {
        _conversations = results[0] as List<ChatConversation>;
        _domains = results[1] as List<String>;
      });
    } on KairoApiException catch (error) {
      if (mounted) setState(() => _runtimeState = _runtimeStateFor(error));
    } catch (_) {
      if (mounted) setState(() => _runtimeState = 'unavailable');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  String _runtimeStateFor(KairoApiException error) {
    if (error.statusCode == 403) return 'disabled';
    return 'unavailable';
  }

  Future<bool> _newConversation() async {
    try {
      final item = await widget.gateway.createConversation(
        _text.newConversation,
      );
      if (!mounted) return false;
      setState(() {
        _conversationId = item.id;
        _conversations = <ChatConversation>[item, ..._conversations];
        _messages = const <ChatMessage>[];
      });
      return true;
    } catch (error) {
      _showError(error);
      return false;
    }
  }

  Future<void> _select(ChatConversation item) async {
    try {
      final detail = await widget.gateway.conversation(item.id);
      if (!mounted) return;
      setState(() {
        _conversationId = detail.id;
        _messages = detail.messages;
        _streamingAnswer = '';
      });
    } catch (error) {
      _showError(error);
    }
  }

  Future<void> _ask() async {
    final question = _questionController.text.trim();
    if (question.isEmpty || _asking) return;
    setState(() {
      _asking = true;
      _streamingAnswer = '';
      _messages = <ChatMessage>[
        ..._messages,
        ChatMessage(
          role: 'user',
          content: question,
          citations: const <ChatCitation>[],
        ),
      ];
      _questionController.clear();
    });
    try {
      if (_conversationId == null && !await _newConversation()) return;
      List<ChatCitation> citations = const <ChatCitation>[];
      await for (final event in widget.gateway.queryStream(
        question: question,
        locale: _localeCode,
        conversationId: _conversationId,
      )) {
        final type = event['type'];
        if (type == 'token') {
          setState(() => _streamingAnswer += event['content'] as String? ?? '');
        } else if (type == 'done') {
          citations =
              (event['citations'] as List<dynamic>? ?? const <dynamic>[])
                  .cast<Map<String, dynamic>>()
                  .map(ChatCitation.fromJson)
                  .toList();
          _conversationId =
              event['conversation_id'] as String? ?? _conversationId;
        } else if (type == 'error') {
          throw KairoApiException(
            statusCode: 503,
            message: event['content'] as String? ?? '',
          );
        }
      }
      if (mounted) {
        setState(() {
          _messages = <ChatMessage>[
            ..._messages,
            ChatMessage(
              role: 'assistant',
              content: _streamingAnswer,
              citations: citations,
            ),
          ];
          _streamingAnswer = '';
        });
      }
    } on KairoApiException catch (error) {
      if (mounted) setState(() => _runtimeState = _runtimeStateFor(error));
    } catch (_) {
      if (mounted) setState(() => _runtimeState = 'unavailable');
    } finally {
      if (mounted) setState(() => _asking = false);
    }
  }

  String get _localeCode => switch (widget.locale) {
    KairoLocale.en => 'en',
    KairoLocale.de => 'de',
    KairoLocale.fr => 'fr',
  };

  void _showError(Object error) {
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text('$error')));
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    if (_runtimeState != null) {
      return Scaffold(
        body: _AiRuntimeState(
          text: _text,
          state: _runtimeState!,
          onRetry: _load,
        ),
      );
    }
    return Scaffold(
      body: SafeArea(
        child: LayoutBuilder(
          builder: (context, constraints) {
            final main = _ChatMain(
              text: _text,
              messages: _messages,
              streamingAnswer: _streamingAnswer,
              questionController: _questionController,
              asking: _asking,
              domains: _domains,
              onAsk: _ask,
            );
            if (constraints.maxWidth < 800) return main;
            return Row(
              children: <Widget>[
                SizedBox(
                  width: 280,
                  child: _ConversationList(
                    text: _text,
                    conversations: _conversations,
                    active: _conversationId,
                    onNew: _newConversation,
                    onSelect: _select,
                  ),
                ),
                const VerticalDivider(width: 1),
                Expanded(child: main),
              ],
            );
          },
        ),
      ),
    );
  }
}

class _ConversationList extends StatelessWidget {
  const _ConversationList({
    required this.text,
    required this.conversations,
    required this.active,
    required this.onNew,
    required this.onSelect,
  });

  final _ChatText text;
  final List<ChatConversation> conversations;
  final String? active;
  final Future<bool> Function() onNew;
  final ValueChanged<ChatConversation> onSelect;

  @override
  Widget build(BuildContext context) => Material(
    color: const Color(0xFFF7F9FC),
    child: ListView(
      padding: const EdgeInsets.all(12),
      children: <Widget>[
        FilledButton.icon(
          onPressed: onNew,
          icon: const Icon(Icons.add),
          label: Text(text.newConversation),
        ),
        const SizedBox(height: 12),
        Text(text.conversations, style: Theme.of(context).textTheme.titleSmall),
        ...conversations.map(
          (item) => ListTile(
            selected: item.id == active,
            title: Text(item.title),
            subtitle: Text('${item.messageCount} ${text.messages}'),
            onTap: () => onSelect(item),
          ),
        ),
      ],
    ),
  );
}

class _ChatMain extends StatelessWidget {
  const _ChatMain({
    required this.text,
    required this.messages,
    required this.streamingAnswer,
    required this.questionController,
    required this.asking,
    required this.domains,
    required this.onAsk,
  });

  final _ChatText text;
  final List<ChatMessage> messages;
  final String streamingAnswer;
  final TextEditingController questionController;
  final bool asking;
  final List<String> domains;
  final VoidCallback onAsk;

  @override
  Widget build(BuildContext context) => Column(
    children: <Widget>[
      Padding(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 8),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            Text(text.kicker, style: Theme.of(context).textTheme.labelLarge),
            Text(text.title, style: Theme.of(context).textTheme.headlineSmall),
            Text(text.lead),
          ],
        ),
      ),
      if (domains.isNotEmpty)
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20),
          child: Wrap(
            spacing: 6,
            children: domains
                .map((item) => Chip(label: Text(item.replaceAll('_', ' '))))
                .toList(),
          ),
        ),
      Expanded(
        child: messages.isEmpty && streamingAnswer.isEmpty
            ? Center(child: Text(text.empty))
            : ListView(
                padding: const EdgeInsets.all(20),
                children: <Widget>[
                  ...messages.map(
                    (message) => _Message(text: text, message: message),
                  ),
                  if (streamingAnswer.isNotEmpty)
                    _Message(
                      text: text,
                      message: ChatMessage(
                        role: 'assistant',
                        content: streamingAnswer,
                        citations: const <ChatCitation>[],
                      ),
                    ),
                ],
              ),
      ),
      Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: <Widget>[
            Expanded(
              child: TextField(
                controller: questionController,
                minLines: 1,
                maxLines: 4,
                decoration: InputDecoration(hintText: text.placeholder),
              ),
            ),
            const SizedBox(width: 8),
            FilledButton(
              onPressed: asking ? null : onAsk,
              child: asking
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.send),
            ),
          ],
        ),
      ),
    ],
  );
}

class _Message extends StatelessWidget {
  const _Message({required this.text, required this.message});
  final _ChatText text;
  final ChatMessage message;

  @override
  Widget build(BuildContext context) {
    final isUser = message.role == 'user';
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Card(
        color: isUser ? const Color(0xFFDDEBFF) : null,
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Text(
                isUser ? text.you : text.assistant,
                style: Theme.of(context).textTheme.labelMedium,
              ),
              Text(message.content),
              if (message.citations.isNotEmpty) ...<Widget>[
                const SizedBox(height: 8),
                Text(
                  text.sources,
                  style: Theme.of(context).textTheme.titleSmall,
                ),
                ...message.citations.map(
                  (citation) => ExpansionTile(
                    title: Text(citation.documentTitle),
                    subtitle: Text(
                      '${(citation.score * 100).toStringAsFixed(0)}%',
                    ),
                    children: <Widget>[
                      Padding(
                        padding: const EdgeInsets.all(12),
                        child: Text(citation.excerpt),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _AiRuntimeState extends StatelessWidget {
  const _AiRuntimeState({
    required this.text,
    required this.state,
    required this.onRetry,
  });
  final _ChatText text;
  final String state;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final disabled = state == 'disabled';
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Card(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: <Widget>[
                Icon(
                  disabled
                      ? Icons.pause_circle_outline
                      : Icons.cloud_off_outlined,
                  size: 48,
                ),
                const SizedBox(height: 12),
                Text(
                  disabled ? text.disabledTitle : text.unavailableTitle,
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 8),
                Text(
                  disabled ? text.disabledLead : text.unavailableLead,
                  textAlign: TextAlign.center,
                ),
                if (!disabled)
                  TextButton.icon(
                    onPressed: onRetry,
                    icon: const Icon(Icons.refresh),
                    label: Text(text.retry),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _ChatText {
  const _ChatText(this.locale);
  final KairoLocale locale;
  bool get _isEnglish => locale == KairoLocale.en;
  bool get _isGerman => locale == KairoLocale.de;
  String get kicker => _isEnglish
      ? 'PRIVATE AI'
      : _isGerman
      ? 'PRIVATE KI'
      : 'IA PRIVÉE';
  String get title => _isEnglish
      ? 'Source-grounded assistant'
      : _isGerman
      ? 'Quellenbasierter Assistent'
      : 'Assistant fondé sur des sources';
  String get lead => _isEnglish
      ? 'Answers are limited to the sources your role is authorised to access.'
      : _isGerman
      ? 'Antworten sind auf Quellen begrenzt, für die Ihre Rolle berechtigt ist.'
      : 'Les réponses sont limitées aux sources autorisées pour votre rôle.';
  String get newConversation => _isEnglish
      ? 'New conversation'
      : _isGerman
      ? 'Neue Unterhaltung'
      : 'Nouvelle conversation';
  String get conversations => _isEnglish
      ? 'Conversations'
      : _isGerman
      ? 'Unterhaltungen'
      : 'Conversations';
  String get messages => _isEnglish
      ? 'messages'
      : _isGerman
      ? 'Nachrichten'
      : 'messages';
  String get empty => _isEnglish
      ? 'Ask a question about information you are authorised to access.'
      : _isGerman
      ? 'Stellen Sie eine Frage zu Informationen, auf die Sie Zugriff haben.'
      : 'Posez une question sur les informations auxquelles vous êtes autorisé.';
  String get placeholder => _isEnglish
      ? 'Ask a question…'
      : _isGerman
      ? 'Frage stellen…'
      : 'Posez une question…';
  String get you => _isEnglish
      ? 'You'
      : _isGerman
      ? 'Sie'
      : 'Vous';
  String get assistant => _isEnglish
      ? 'Assistant'
      : _isGerman
      ? 'Assistent'
      : 'Assistant';
  String get sources => _isEnglish
      ? 'Sources'
      : _isGerman
      ? 'Quellen'
      : 'Sources';
  String get disabledTitle => _isEnglish
      ? 'Assistant disabled'
      : _isGerman
      ? 'Assistent deaktiviert'
      : 'Assistant IA désactivé';
  String get disabledLead => _isEnglish
      ? 'The association has disabled the private AI assistant.'
      : _isGerman
      ? 'Der Verein hat den privaten KI-Assistenten deaktiviert.'
      : 'L’association a désactivé l’assistant IA privé.';
  String get unavailableTitle => _isEnglish
      ? 'Assistant temporarily unavailable'
      : _isGerman
      ? 'Assistent vorübergehend nicht verfügbar'
      : 'Assistant temporairement indisponible';
  String get unavailableLead => _isEnglish
      ? 'The private AI runtime cannot currently be reached. Your business data remains available.'
      : _isGerman
      ? 'Die private KI-Laufzeit ist derzeit nicht erreichbar. Ihre Geschäftsdaten bleiben verfügbar.'
      : 'Le runtime IA privé est momentanément indisponible. Vos données métier restent disponibles.';
  String get retry => _isEnglish
      ? 'Retry'
      : _isGerman
      ? 'Erneut versuchen'
      : 'Réessayer';
}
