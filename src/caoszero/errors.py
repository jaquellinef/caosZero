"""Exceções de domínio do CaosZero."""


class CaosZeroError(Exception):
    """Erro esperado da aplicação, exibido de forma amigável na CLI."""


class ConfigError(CaosZeroError):
    """Configuração ausente, inválida ou incompatível."""


class PlanError(CaosZeroError):
    """Não foi possível montar um plano de operações seguro."""


class JournalError(CaosZeroError):
    """Falha ao ler ou gravar o histórico de execuções."""
