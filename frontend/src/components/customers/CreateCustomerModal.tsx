import { useEffect, useState } from "react";
import { createCustomer } from "../../api";
import type { Lang } from "../../i18n";
import { t } from "../../i18n";

import Button from "../Button";
import ErrorMessage from "../ErrorMessage";
import Input from "../Input";
import Modal from "../Modal";

type CreateCustomerModalProps = {
  lang: Lang;
  open: boolean;
  onClose: () => void;
  onCreated: () => void | Promise<void>;
};

export default function CreateCustomerModal({
  lang,
  open,
  onClose,
  onCreated,
}: CreateCustomerModalProps) {
  const [customerId, setCustomerId] = useState("");
  const [accountName, setAccountName] = useState("");
  const [country, setCountry] = useState("");

  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) {
      setCustomerId("");
      setAccountName("");
      setCountry("");
      setError(null);
      setCreating(false);
    }
  }, [open]);

  if (!open) {
    return null;
  }

  function handleClose() {
    if (creating) {
      return;
    }

    onClose();
  }

  async function handleSubmit(
    e: React.FormEvent<HTMLFormElement>,
  ) {
    e.preventDefault();

    setError(null);
    setCreating(true);

    try {
      await createCustomer({
        customer_id: customerId,
        account_name: accountName,
        country: country || null,
      });

      await onCreated();

      onClose();
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "Create failed",
      );
    } finally {
      setCreating(false);
    }
  }

  return (
    <Modal
      title={t(lang, "cust_create")}
      onClose={handleClose}
    >
      <form onSubmit={handleSubmit}>
        <div className="space-y-4">
          {error && <ErrorMessage>{error}</ErrorMessage>}

          <Input
            autoFocus
            label={t(lang, "cust_col_sap")}
            placeholder={t(lang, "cust_id_ph")}
            value={customerId}
            onChange={(e) => setCustomerId(e.target.value)}
            className="bg-blue-50 font-mono"
            required
            disabled={creating}
          />

          <Input
            label={t(lang, "cust_name_ph")}
            placeholder={t(lang, "cust_name_ph")}
            value={accountName}
            onChange={(e) => setAccountName(e.target.value)}
            required
            disabled={creating}
          />

          <Input
            label={t(lang, "cust_col_country")}
            placeholder={t(lang, "cust_country_ph")}
            value={country}
            onChange={(e) => setCountry(e.target.value)}
            disabled={creating}
          />
        </div>

        <div className="flex justify-end gap-2 mt-5 pt-4 border-t">
          <Button
            type="button"
            variant="secondary"
            onClick={handleClose}
            disabled={creating}
          >
            Cancel
          </Button>

          <Button
            type="submit"
            disabled={creating}
          >
            {creating
              ? t(lang, "cust_loading")
              : t(lang, "cust_create")}
          </Button>
        </div>
      </form>
    </Modal>
  );
}