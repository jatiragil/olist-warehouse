from src.utils.logger import get_logger

logger = get_logger(__name__)


def validate_rows(rows, table_name, pk_columns=None, not_null_columns=None):
    """
    Validasi list of tuples sebelum insert ke warehouse.

    Args:
        rows: List of tuples.
        table_name: Nama tabel (untuk log).
        pk_columns: Index kolom yang membentuk PK. Default [0].
        not_null_columns: Index kolom yang tidak boleh NULL. Default [0].
    """
    if pk_columns is None:
        pk_columns = [0]
    if not_null_columns is None:
        not_null_columns = [0]

    logger.info(f"Validasi data untuk {table_name}")

    # Cek 1: rows tidak kosong
    if not rows:
        raise ValueError(f"{table_name}: rows kosong!")

    # Cek 2: tidak ada NULL di kolom penting
    null_count = 0
    for i, row in enumerate(rows):
        for col in not_null_columns:
            if row[col] is None:
                null_count += 1
                if null_count <= 5:
                    logger.warning(
                        f"{table_name}: NULL di baris {i}, kolom {col}: {row}"
                    )
                break

    if null_count > 0:
        logger.warning(f"{table_name}: {null_count} baris dengan NULL")

    # Cek 3: tidak ada duplikat berdasarkan PK
    seen = set()
    duplicates = 0
    for row in rows:
        key = tuple(row[i] for i in pk_columns)
        if key in seen:
            duplicates += 1
        else:
            seen.add(key)

    if duplicates > 0:
        logger.warning(
            f"{table_name}: {duplicates} duplikat berdasarkan PK {pk_columns}"
        )

    # Ringkasan
    logger.info(
        f"{table_name}: validasi selesai. "
        f"Total: {len(rows):,}, NULL: {null_count}, Duplikat: {duplicates}"
    )