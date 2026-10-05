import Button from "../Button";
import type { CustomerDetail as CustomerDetailData } from "../../api";
import { t, type Lang } from "../../i18n";

type CustomerDetailProps = {
  lang: Lang;
  detail: CustomerDetailData | null;
  loading: boolean;
  error: string | null;
  onClose: () => void;
};

export default function CustomerDetail({
  lang,
  detail,
  loading,
  error,
  onClose,
}: CustomerDetailProps) {
  if (loading) {
    return (
      <p className="text-sm text-gray-500">
        {t(lang, "cust_loading")}
      </p>
    );
  }

  if (error) {
    return (
      <p className="text-sm text-red-600">
        {error}
      </p>
    );
  }

  if (!detail) {
    return null;
  }

  return (
    <div className="space-y-3">
      {/* Address */}
      <div>
        <div className="text-xs font-bold text-gray-500 uppercase mb-1">
          {t(lang, "cust_addr_title")}
        </div>

        {detail.sites.length === 0 ? (
          <p className="text-sm text-gray-500">
            {t(lang, "cust_no_addr")}
          </p>
        ) : (
          detail.sites.map((site) => (
            <div key={site.id} className="text-sm">
              {[
                site.physical_street,
                [
                  site.physical_postal_code,
                  site.physical_city,
                ]
                  .filter(Boolean)
                  .join(" "),
                site.physical_province,
                site.physical_country,
              ]
                .filter(Boolean)
                .join(", ")}
            </div>
          ))
        )}
      </div>

      {/* Machines */}
      <div>
        <div className="text-xs font-bold text-gray-500 uppercase mb-1">
          {t(lang, "cust_machines_title")} ({detail.machines.length})
        </div>

        {detail.machines.length === 0 ? (
          <p className="text-sm text-gray-500">
            {t(lang, "cust_no_machines")}
          </p>
        ) : (
          <div className="overflow-auto max-h-96 bg-white rounded border">
            <table className="w-full text-xs">
              <thead className="sticky top-0">
                <tr className="bg-gray-100 text-left">
                  <th className="px-2 py-1.5 font-semibold">
                    {t(lang, "cust_col_machine")}
                  </th>
                  <th className="px-2 py-1.5 font-semibold">
                    {t(lang, "cust_col_line")}
                  </th>
                  <th className="px-2 py-1.5 font-semibold">
                    {t(lang, "cust_col_component")}
                  </th>
                  <th className="px-2 py-1.5 font-semibold">
                    {t(lang, "cust_col_material")}
                  </th>
                </tr>
              </thead>

              <tbody>
                {detail.machines.map((machine) =>
                  machine.components.map((component, index) => (
                    <tr
                      key={`${machine.equipment_name}-${index}`}
                      className="border-b last:border-0"
                    >
                      <td className="px-2 py-1 font-mono font-semibold text-weber-blue">
                        {index === 0
                          ? machine.equipment_name
                          : ""}
                      </td>

                      <td className="px-2 py-1 text-gray-600">
                        {index === 0
                          ? machine.machine_type ?? "—"
                          : ""}
                      </td>

                      <td className="px-2 py-1">
                        {component.component_type ?? "—"}
                      </td>

                      <td className="px-2 py-1 font-mono text-gray-700">
                        {component.material_no ?? "—"}
                      </td>
                    </tr>
                  )),
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <Button
        type="button"
        variant="ghost"
        size="sm"
        onClick={onClose}
        className="text-blue-600 hover:underline"
      >
        {t(lang, "cust_close_detail")}
      </Button>
    </div>
  );
}