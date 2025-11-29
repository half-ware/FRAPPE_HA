app_name = "frappe_ha"
app_title = "Frappe HA"
app_publisher = "Said TAZI"
app_description = "Frappe HA"
app_email = "contact@half-ware.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "frappe_ha",
# 		"logo": "/assets/frappe_ha/logo.png",
# 		"title": "Frappe HA",
# 		"route": "/frappe_ha",
# 		"has_permission": "frappe_ha.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/frappe_ha/css/frappe_ha.css"
# app_include_js = "/assets/frappe_ha/js/frappe_ha.js"

# include js, css files in header of web template
# web_include_css = "/assets/frappe_ha/css/frappe_ha.css"
# web_include_js = "/assets/frappe_ha/js/frappe_ha.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "frappe_ha/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "frappe_ha/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "frappe_ha.utils.jinja_methods",
# 	"filters": "frappe_ha.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "frappe_ha.install.before_install"
# after_install = "frappe_ha.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "frappe_ha.uninstall.before_uninstall"
# after_uninstall = "frappe_ha.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "frappe_ha.utils.before_app_install"
# after_app_install = "frappe_ha.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "frappe_ha.utils.before_app_uninstall"
# after_app_uninstall = "frappe_ha.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "frappe_ha.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"*": {
#		"before_insert": "frappe_ha.sync_service.enqueue_before_insert",
		"after_insert": "frappe_ha.sync_service.enqueue_after_insert",
		"on_update": "frappe_ha.sync_service.enqueue_update",
#		"before_submit": "frappe_ha.sync_service.enqueue_before_submit",
		"on_submit": "frappe_ha.sync_service.enqueue_submit",
#		"before_cancel": "frappe_ha.sync_service.enqueue_before_cancel",
		"on_cancel": "frappe_ha.sync_service.enqueue_cancel",
#		"before_delete": "frappe_ha.sync_service.enqueue_pre_delete",
		"on_trash": "frappe_ha.sync_service.enqueue_delete",
	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"all": [
		"frappe_ha.sync_service.process_queue"
	],
# 	"daily": [
# 		"frappe_ha.tasks.daily"
# 	],
# 	"hourly": [
# 		"frappe_ha.tasks.hourly"
# 	],
# 	"weekly": [
# 		"frappe_ha.tasks.weekly"
# 	],
# 	"monthly": [
# 		"frappe_ha.tasks.monthly"
# 	],
}

# Testing
# -------

# before_tests = "frappe_ha.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "frappe_ha.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "frappe_ha.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["frappe_ha.utils.before_request"]
# after_request = ["frappe_ha.utils.after_request"]

# Job Events
# ----------
# before_job = ["frappe_ha.utils.before_job"]
# after_job = ["frappe_ha.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"frappe_ha.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

