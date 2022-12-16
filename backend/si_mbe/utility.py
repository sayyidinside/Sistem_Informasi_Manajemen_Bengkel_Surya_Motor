from si_mbe.models import Logs


def perform_log(request: any, operation: str, table_name: str) -> None:
    Logs.objects.create(
        user_id=request.user,
        operation=operation,
        table_name=table_name,
    )
