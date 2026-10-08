import type { Customer, CustomerDetail } from "../../api";
import type { Lang } from "../../i18n";
import { t } from "../../i18n";

import DataTable from "../DataTable";
import Input from "../Input";
import Pagination from "../Pagination";
import CustomerDetailView from "./CustomerDetail";

type CustomerTableProps = {
  lang: Lang;
  data: Customer[];
  loading: boolean;

  search: string;
  onSearchChange: (value: string) => void;

  selectedId: string | null;
  onSelect: (id: string | null) => void;

  detail: CustomerDetail | null;
  detailLoading: boolean;
  detailError: string | null;

  page: number;
  total: number;
  onPageChange: (page: number) => void;
};

const PAGE_SIZE = 50;

export default function CustomerTable({
  lang,
  data,
  loading,
  search,
  onSearchChange,
  selectedId,
  onSelect,
  detail,
  detailLoading,
  detailError,
  page,
  total,
  onPageChange,
}: CustomerTableProps) {
  function toggleCustomer(id: string) {
    onSelect(selectedId === id ? null : id);
  }

  function closeDetail() {
    onSelect(null);
  }

  const columns = [
    {
      accessorKey: "customer_id",
      header: t(lang, "cust_col_sap"),
      cell: ({ row }: any) => (
        <span className="font-mono font-semibold text-weber-blue">
          {row.original.customer_id}
        </span>
      ),
    },
    {
      accessorKey: "account_name",
      header: t(lang, "cust_name_ph"),
    },
    {
      accessorKey: "country",
      header: t(lang, "cust_col_country"),
      cell: ({ row }: any) => (
        <span className="text-gray-600">
          {row.original.country ?? "—"}
        </span>
      ),
    },
  ];

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-2">
      <Input
        placeholder={t(lang, "cust_search_ph")}
        value={search}
        onChange={(e) => onSearchChange(e.target.value)}
      />

      <Pagination
        page={page}
        pageSize={PAGE_SIZE}
        total={total}
        onPageChange={onPageChange}
      />

      <DataTable
        data={data}
        columns={columns}
        loading={loading}
        loadingText={t(lang, "cust_loading")}
        getRowId={(customer) => customer.customer_id}
        selectedRowId={selectedId}
        onRowClick={(customer) =>
          toggleCustomer(customer.customer_id)
        }
        renderExpandedRow={(customer) => (
          <CustomerDetailView
            lang={lang}
            detail={detail}
            loading={
              selectedId === customer.customer_id &&
              detailLoading
            }
            error={
              selectedId === customer.customer_id
                ? detailError
                : null
            }
            onClose={closeDetail}
          />
        )}
      />
    </div>
  );
}