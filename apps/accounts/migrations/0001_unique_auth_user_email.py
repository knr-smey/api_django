from django.db import migrations


def normalize_and_check_existing_emails(apps, schema_editor):
	User = apps.get_model("auth", "User")

	normalized_rows = []
	for user_id, email in User.objects.order_by("id").values_list("id", "email"):
		normalized_rows.append((user_id, email, (email or "").strip().lower()))

	blank_email_ids = [user_id for user_id, _, normalized_email in normalized_rows if not normalized_email]
	if blank_email_ids:
		raise RuntimeError(
			"Cannot add a unique index to auth_user.email while users have blank emails. "
			f"Update or remove these auth_user IDs first: {blank_email_ids}"
		)

	seen = {}
	duplicates = {}
	for user_id, _, normalized_email in normalized_rows:
		if normalized_email in seen:
			duplicates.setdefault(normalized_email, [seen[normalized_email]]).append(user_id)
		else:
			seen[normalized_email] = user_id

	if duplicates:
		details = ", ".join(
			f"{email}: IDs {ids}" for email, ids in duplicates.items()
		)
		raise RuntimeError(
			"Cannot add a unique index to auth_user.email while duplicate emails exist. "
			"Merge, delete, or change duplicate accounts before running migrations. "
			f"Duplicates: {details}"
		)

	for user_id, email, normalized_email in normalized_rows:
		if email != normalized_email:
			User.objects.filter(id=user_id).update(email=normalized_email)


class Migration(migrations.Migration):
	dependencies = [
		("auth", "0012_alter_user_first_name_max_length"),
	]

	operations = [
		migrations.RunPython(
			normalize_and_check_existing_emails,
			reverse_code=migrations.RunPython.noop,
		),
		migrations.RunSQL(
			sql=(
				"CREATE UNIQUE INDEX auth_user_email_unique "
				"ON auth_user (email)"
			),
			reverse_sql="DROP INDEX auth_user_email_unique ON auth_user",
		),
	]
