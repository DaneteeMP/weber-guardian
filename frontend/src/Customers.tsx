import { useEffect, useState } from "react";

import {
  getCustomerDetail,
  listCustomers,
  type Customer,
  type CustomerDetail,
} from "./api";

import Button from "./components/Button";
import CreateCustomerModal from "./components/customers/CreateCustomerModal";
import CustomerTable from "./components/customers/CustomerTable";
import ErrorMessage from "./components/ErrorMessage";
import PageHeader from "./components/PageHeader";
import SectionCard from "./components/SectionCard";

import { t, type Lang } from "./i18n";

const PAGE_SIZE = 50;

export default function Customers({
  lang,
  externalSearch = "",
}: {
  lang: Lang;
  externalSearch?: string;
}) {
  const [rows, setRows] = useState<Customer[]>([]);
  const [total, setTotal] = useState(0);

  const [page, setPage] = useState(0);
  const [search, setSearch] = useState(externalSearch);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<CustomerDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);

  const [showCreateModal, setShowCreateModal] = useState(false);

  async function load(q: string, p: number) {
    setLoading(true);
    setError(null);

    try {
      const res = await listCustomers({
        search: q.trim() || undefined,
        limit: PAGE_SIZE,
        offset: p * PAGE_SIZE,
      });

      setRows(res.rows);
      setTotal(res.total);
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "Load failed",
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleSearchChange(value: string) {
    setSearch(value);
    setPage(0);
  }

  async function handlePageChange(nextPage: number) {
    setPage(nextPage);
    await load(search, nextPage);
  }

  async function handleSelectCustomer(id: string | null) {
    if (!id) {
      setSelectedId(null);
      setDetail(null);
      setDetailError(null);
      return;
    }

    setSelectedId(id);
    setDetail(null);
    setDetailError(null);
    setDetailLoading(true);

    try {
      setDetail(await getCustomerDetail(id));
    } catch (e) {
      setDetailError(
        e instanceof Error ? e.message : "Detail failed",
      );
    } finally {
      setDetailLoading(false);
    }
  }

  async function handleCreated() {
    setPage(0);
    await load(search, 0);
  }

  useEffect(() => {
    const timer = setTimeout(() => {
      load(search, 0);
    }, 300);

    return () => clearTimeout(timer);

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search]);

  return (
    <div className="p-4 space-y-3 w-full h-full">
      <PageHeader
        title={t(lang, "cust_title")}
        action={
          <Button
            onClick={() => setShowCreateModal(true)}
          >
            + {t(lang, "cust_create")}
          </Button>
        }
      />

      {error && (
        <ErrorMessage>
          {error}
        </ErrorMessage>
      )}

      <SectionCard
        title={`${t(lang, "nav_customers")} (${total.toLocaleString()})`}
      >
        <CustomerTable
          lang={lang}
          data={rows}
          loading={loading}
          search={search}
          onSearchChange={handleSearchChange}
          selectedId={selectedId}
          onSelect={handleSelectCustomer}
          detail={detail}
          detailLoading={detailLoading}
          detailError={detailError}
          page={page}
          total={total}
          onPageChange={handlePageChange}
        />
      </SectionCard>

      <CreateCustomerModal
        lang={lang}
        open={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onCreated={handleCreated}
      />
    </div>
  );
}
