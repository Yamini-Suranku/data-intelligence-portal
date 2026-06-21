// Precomputed sample-repo scan result for the static (no-backend) demo on GitHub Pages.
// Generated from `POST /api/scan/demo` (the bundled Postgres SQL+Tableau+PowerBI sample).
window.SAMPLE_SCAN = {
  "summary": {
    "files": 8,
    "tables": 12,
    "columns": 33
  },
  "dataLineage": [
    {
      "source": "public.regions",
      "target": "analytics.dim_customer",
      "relation": "derived_from"
    },
    {
      "source": "stg_customers",
      "target": "analytics.dim_customer",
      "relation": "derived_from"
    },
    {
      "source": "stg_orders",
      "target": "analytics.fct_orders",
      "relation": "derived_from"
    },
    {
      "source": "stg_payments",
      "target": "analytics.fct_orders",
      "relation": "derived_from"
    },
    {
      "source": "analytics.dim_customer",
      "target": "analytics.mart_revenue",
      "relation": "derived_from"
    },
    {
      "source": "analytics.fct_orders",
      "target": "analytics.mart_revenue",
      "relation": "derived_from"
    },
    {
      "source": "analytics.dim_customer",
      "target": "exec_dashboard",
      "relation": "reads"
    },
    {
      "source": "analytics.mart_revenue",
      "target": "exec_dashboard",
      "relation": "reads"
    },
    {
      "source": "analytics.mart_revenue",
      "target": "sales_overview",
      "relation": "derived_from"
    },
    {
      "source": "public.regions",
      "target": "sales_overview",
      "relation": "reads"
    },
    {
      "source": "public.customers",
      "target": "stg_customers",
      "relation": "derived_from"
    },
    {
      "source": "public.orders",
      "target": "stg_orders",
      "relation": "derived_from"
    },
    {
      "source": "public.payments",
      "target": "stg_payments",
      "relation": "derived_from"
    }
  ],
  "processLineage": [
    {
      "marker_id": "scan \u00b7 Sample (Postgres)",
      "run_id": "86bd3d1946c649dfa3fd1161c6a9fdca",
      "step_name": "repo_fetched",
      "detail": "local_path: sample"
    },
    {
      "marker_id": "scan \u00b7 Sample (Postgres)",
      "run_id": "86bd3d1946c649dfa3fd1161c6a9fdca",
      "step_name": "files_parsed",
      "detail": "8 file(s): 6 SQL, 2 report(s)"
    },
    {
      "marker_id": "scan \u00b7 Sample (Postgres)",
      "run_id": "86bd3d1946c649dfa3fd1161c6a9fdca",
      "step_name": "tables_extracted",
      "detail": "12 table(s)"
    },
    {
      "marker_id": "scan \u00b7 Sample (Postgres)",
      "run_id": "86bd3d1946c649dfa3fd1161c6a9fdca",
      "step_name": "column_lineage_built",
      "detail": "33 column link(s)"
    }
  ],
  "tables": [
    "analytics.dim_customer",
    "analytics.fct_orders",
    "analytics.mart_revenue",
    "exec_dashboard",
    "sales_overview",
    "stg_customers",
    "stg_orders",
    "stg_payments"
  ],
  "columns": {
    "analytics.dim_customer": [
      {
        "target_table": "analytics.dim_customer",
        "target_column": "customer_id",
        "source_table": "stg_customers",
        "source_column": "customer_id",
        "transformation": "c.customer_id AS customer_id"
      },
      {
        "target_table": "analytics.dim_customer",
        "target_column": "email",
        "source_table": "stg_customers",
        "source_column": "email",
        "transformation": "c.email AS email"
      },
      {
        "target_table": "analytics.dim_customer",
        "target_column": "full_name",
        "source_table": "stg_customers",
        "source_column": "full_name",
        "transformation": "c.full_name AS full_name"
      },
      {
        "target_table": "analytics.dim_customer",
        "target_column": "region_name",
        "source_table": "public.regions",
        "source_column": "region_name",
        "transformation": "r.region_name AS region_name"
      },
      {
        "target_table": "analytics.mart_revenue",
        "target_column": "region_name",
        "source_table": "analytics.dim_customer",
        "source_column": "region_name",
        "transformation": "d.region_name AS region_name"
      }
    ],
    "analytics.fct_orders": [
      {
        "target_table": "analytics.fct_orders",
        "target_column": "balance_due",
        "source_table": "stg_orders",
        "source_column": "order_total",
        "transformation": "(o.order_total - COALESCE(p.paid_amount, 0)) AS balance_due"
      },
      {
        "target_table": "analytics.fct_orders",
        "target_column": "balance_due",
        "source_table": "stg_payments",
        "source_column": "amount",
        "transformation": "(o.order_total - COALESCE(p.paid_amount, 0)) AS balance_due"
      },
      {
        "target_table": "analytics.fct_orders",
        "target_column": "customer_id",
        "source_table": "stg_orders",
        "source_column": "customer_id",
        "transformation": "o.customer_id AS customer_id"
      },
      {
        "target_table": "analytics.fct_orders",
        "target_column": "order_date",
        "source_table": "stg_orders",
        "source_column": "order_date",
        "transformation": "o.order_date AS order_date"
      },
      {
        "target_table": "analytics.fct_orders",
        "target_column": "order_id",
        "source_table": "stg_orders",
        "source_column": "order_id",
        "transformation": "o.order_id AS order_id"
      },
      {
        "target_table": "analytics.fct_orders",
        "target_column": "order_total",
        "source_table": "stg_orders",
        "source_column": "order_total",
        "transformation": "o.order_total AS order_total"
      },
      {
        "target_table": "analytics.fct_orders",
        "target_column": "paid_amount",
        "source_table": "stg_payments",
        "source_column": "amount",
        "transformation": "COALESCE(p.paid_amount, 0) AS paid_amount"
      },
      {
        "target_table": "analytics.mart_revenue",
        "target_column": "order_count",
        "source_table": "analytics.fct_orders",
        "source_column": "order_id",
        "transformation": "COUNT(DISTINCT f.order_id) AS order_count"
      },
      {
        "target_table": "analytics.mart_revenue",
        "target_column": "revenue",
        "source_table": "analytics.fct_orders",
        "source_column": "paid_amount",
        "transformation": "SUM(f.paid_amount) AS revenue"
      }
    ],
    "analytics.mart_revenue": [
      {
        "target_table": "analytics.mart_revenue",
        "target_column": "order_count",
        "source_table": "analytics.fct_orders",
        "source_column": "order_id",
        "transformation": "COUNT(DISTINCT f.order_id) AS order_count"
      },
      {
        "target_table": "analytics.mart_revenue",
        "target_column": "region_name",
        "source_table": "analytics.dim_customer",
        "source_column": "region_name",
        "transformation": "d.region_name AS region_name"
      },
      {
        "target_table": "analytics.mart_revenue",
        "target_column": "revenue",
        "source_table": "analytics.fct_orders",
        "source_column": "paid_amount",
        "transformation": "SUM(f.paid_amount) AS revenue"
      },
      {
        "target_table": "exec_dashboard",
        "target_column": "Avg Orders",
        "source_table": "analytics.mart_revenue",
        "source_column": null,
        "transformation": "AVERAGE('analytics.mart_revenue'[order_count])"
      },
      {
        "target_table": "exec_dashboard",
        "target_column": "Total Revenue",
        "source_table": "analytics.mart_revenue",
        "source_column": null,
        "transformation": "SUM('analytics.mart_revenue'[revenue])"
      },
      {
        "target_table": "sales_overview",
        "target_column": "order_count",
        "source_table": "analytics.mart_revenue",
        "source_column": "order_count",
        "transformation": "mart_revenue.order_count AS order_count"
      },
      {
        "target_table": "sales_overview",
        "target_column": "region_name",
        "source_table": "analytics.mart_revenue",
        "source_column": "region_name",
        "transformation": "mart_revenue.region_name AS region_name"
      },
      {
        "target_table": "sales_overview",
        "target_column": "revenue",
        "source_table": "analytics.mart_revenue",
        "source_column": "revenue",
        "transformation": "mart_revenue.revenue AS revenue"
      }
    ],
    "exec_dashboard": [
      {
        "target_table": "exec_dashboard",
        "target_column": "Avg Orders",
        "source_table": "analytics.mart_revenue",
        "source_column": null,
        "transformation": "AVERAGE('analytics.mart_revenue'[order_count])"
      },
      {
        "target_table": "exec_dashboard",
        "target_column": "Total Revenue",
        "source_table": "analytics.mart_revenue",
        "source_column": null,
        "transformation": "SUM('analytics.mart_revenue'[revenue])"
      }
    ],
    "sales_overview": [
      {
        "target_table": "sales_overview",
        "target_column": "Avg Order Value",
        "source_table": null,
        "source_column": null,
        "transformation": "[revenue] / [order_count]"
      },
      {
        "target_table": "sales_overview",
        "target_column": "order_count",
        "source_table": "analytics.mart_revenue",
        "source_column": "order_count",
        "transformation": "mart_revenue.order_count AS order_count"
      },
      {
        "target_table": "sales_overview",
        "target_column": "region_name",
        "source_table": "analytics.mart_revenue",
        "source_column": "region_name",
        "transformation": "mart_revenue.region_name AS region_name"
      },
      {
        "target_table": "sales_overview",
        "target_column": "revenue",
        "source_table": "analytics.mart_revenue",
        "source_column": "revenue",
        "transformation": "mart_revenue.revenue AS revenue"
      }
    ],
    "stg_customers": [
      {
        "target_table": "analytics.dim_customer",
        "target_column": "customer_id",
        "source_table": "stg_customers",
        "source_column": "customer_id",
        "transformation": "c.customer_id AS customer_id"
      },
      {
        "target_table": "analytics.dim_customer",
        "target_column": "email",
        "source_table": "stg_customers",
        "source_column": "email",
        "transformation": "c.email AS email"
      },
      {
        "target_table": "analytics.dim_customer",
        "target_column": "full_name",
        "source_table": "stg_customers",
        "source_column": "full_name",
        "transformation": "c.full_name AS full_name"
      },
      {
        "target_table": "stg_customers",
        "target_column": "customer_id",
        "source_table": "public.customers",
        "source_column": "customer_id",
        "transformation": "c.customer_id AS customer_id"
      },
      {
        "target_table": "stg_customers",
        "target_column": "email",
        "source_table": "public.customers",
        "source_column": "email",
        "transformation": "c.email AS email"
      },
      {
        "target_table": "stg_customers",
        "target_column": "full_name",
        "source_table": "public.customers",
        "source_column": "full_name",
        "transformation": "c.full_name AS full_name"
      },
      {
        "target_table": "stg_customers",
        "target_column": "region_id",
        "source_table": "public.customers",
        "source_column": "region_id",
        "transformation": "c.region_id AS region_id"
      }
    ],
    "stg_orders": [
      {
        "target_table": "analytics.fct_orders",
        "target_column": "balance_due",
        "source_table": "stg_orders",
        "source_column": "order_total",
        "transformation": "(o.order_total - COALESCE(p.paid_amount, 0)) AS balance_due"
      },
      {
        "target_table": "analytics.fct_orders",
        "target_column": "customer_id",
        "source_table": "stg_orders",
        "source_column": "customer_id",
        "transformation": "o.customer_id AS customer_id"
      },
      {
        "target_table": "analytics.fct_orders",
        "target_column": "order_date",
        "source_table": "stg_orders",
        "source_column": "order_date",
        "transformation": "o.order_date AS order_date"
      },
      {
        "target_table": "analytics.fct_orders",
        "target_column": "order_id",
        "source_table": "stg_orders",
        "source_column": "order_id",
        "transformation": "o.order_id AS order_id"
      },
      {
        "target_table": "analytics.fct_orders",
        "target_column": "order_total",
        "source_table": "stg_orders",
        "source_column": "order_total",
        "transformation": "o.order_total AS order_total"
      },
      {
        "target_table": "stg_orders",
        "target_column": "customer_id",
        "source_table": "public.orders",
        "source_column": "customer_id",
        "transformation": "o.customer_id AS customer_id"
      },
      {
        "target_table": "stg_orders",
        "target_column": "order_date",
        "source_table": "public.orders",
        "source_column": "created_at",
        "transformation": "CAST(o.created_at AS DATE) AS order_date"
      },
      {
        "target_table": "stg_orders",
        "target_column": "order_id",
        "source_table": "public.orders",
        "source_column": "order_id",
        "transformation": "o.order_id AS order_id"
      },
      {
        "target_table": "stg_orders",
        "target_column": "order_status",
        "source_table": "public.orders",
        "source_column": "order_status",
        "transformation": "o.order_status AS order_status"
      },
      {
        "target_table": "stg_orders",
        "target_column": "order_total",
        "source_table": "public.orders",
        "source_column": "order_total",
        "transformation": "o.order_total AS order_total"
      }
    ],
    "stg_payments": [
      {
        "target_table": "analytics.fct_orders",
        "target_column": "balance_due",
        "source_table": "stg_payments",
        "source_column": "amount",
        "transformation": "(o.order_total - COALESCE(p.paid_amount, 0)) AS balance_due"
      },
      {
        "target_table": "analytics.fct_orders",
        "target_column": "paid_amount",
        "source_table": "stg_payments",
        "source_column": "amount",
        "transformation": "COALESCE(p.paid_amount, 0) AS paid_amount"
      },
      {
        "target_table": "stg_payments",
        "target_column": "amount",
        "source_table": "public.payments",
        "source_column": "amount",
        "transformation": "p.amount AS amount"
      },
      {
        "target_table": "stg_payments",
        "target_column": "order_id",
        "source_table": "public.payments",
        "source_column": "order_id",
        "transformation": "p.order_id AS order_id"
      },
      {
        "target_table": "stg_payments",
        "target_column": "payment_date",
        "source_table": "public.payments",
        "source_column": "captured_at",
        "transformation": "CAST(p.captured_at AS DATE) AS payment_date"
      },
      {
        "target_table": "stg_payments",
        "target_column": "payment_id",
        "source_table": "public.payments",
        "source_column": "payment_id",
        "transformation": "p.payment_id AS payment_id"
      }
    ]
  }
};
