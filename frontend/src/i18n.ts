// F2 i18n: plain dictionaries, no library.
// Five languages were explicitly requested (ES/EN/DE/PT/IT); a library
// would add weight for what is a static lookup table.
export type Lang = "es" | "en" | "de" | "pt" | "it";

export const LANGS: { code: Lang; label: string }[] = [
  { code: "es", label: "ES" },
  { code: "en", label: "EN" },
  { code: "de", label: "DE" },
  { code: "pt", label: "PT" },
  { code: "it", label: "IT" },
];

const es = {
  nav_offers: "Ofertas Guardian",
  nav_customers: "Clientes",
  cust_title: "Clientes (F0)",
  cust_id_ph: "SAP Debitor ID (customer_id)",
  cust_name_ph: "Nombre de cuenta",
  cust_country_ph: "País (opcional)",
  cust_create: "Crear",
  cust_loading: "Cargando…",
  ob_title: "OFERTA GUARDIAN",
  ob_save: "GUARDAR OFERTA",
  ob_customer_offer: "Cliente y oferta",
  ob_hours_travel: "Horas y viaje",
  ob_breakdown: "Desglose (del backend)",
  ob_items: "Líneas",
  ob_add_line: "+ Añadir línea",
  ob_remove: "Quitar",
  ob_saved: "Oferta guardada",
  ob_select_client: "Elige cliente...",
  ob_select_first: "Selecciona un cliente primero",
};

export type Strings = typeof es;

const en: Strings = {
  nav_offers: "Guardian offers",
  nav_customers: "Customers",
  cust_title: "Customers (F0)",
  cust_id_ph: "SAP Debitor ID (customer_id)",
  cust_name_ph: "Account Name",
  cust_country_ph: "Country (optional)",
  cust_create: "Create",
  cust_loading: "Loading…",
  ob_title: "GUARDIAN OFFER",
  ob_save: "SAVE OFFER",
  ob_customer_offer: "Customer & offer",
  ob_hours_travel: "Hours & travel input",
  ob_breakdown: "Breakdown (from backend)",
  ob_items: "Items",
  ob_add_line: "+ Add line",
  ob_remove: "Remove",
  ob_saved: "Offer saved",
  ob_select_client: "Select client...",
  ob_select_first: "Select a customer first",
};

const de: Strings = {
  nav_offers: "Guardian-Angebote",
  nav_customers: "Kunden",
  cust_title: "Kunden (F0)",
  cust_id_ph: "SAP-Debitor-ID (customer_id)",
  cust_name_ph: "Kontiname",
  cust_country_ph: "Land (optional)",
  cust_create: "Anlegen",
  cust_loading: "Lädt…",
  ob_title: "GUARDIAN-ANGEBOT",
  ob_save: "ANGEBOT SPEICHERN",
  ob_customer_offer: "Kunde & Angebot",
  ob_hours_travel: "Stunden & Reise",
  ob_breakdown: "Aufschlüsselung (vom Backend)",
  ob_items: "Positionen",
  ob_add_line: "+ Position hinzufügen",
  ob_remove: "Entfernen",
  ob_saved: "Angebot gespeichert",
  ob_select_client: "Kunde wählen...",
  ob_select_first: "Bitte zuerst einen Kunden wählen",
};

const pt: Strings = {
  nav_offers: "Ofertas Guardian",
  nav_customers: "Clientes",
  cust_title: "Clientes (F0)",
  cust_id_ph: "SAP Debitor ID (customer_id)",
  cust_name_ph: "Nome da conta",
  cust_country_ph: "País (opcional)",
  cust_create: "Criar",
  cust_loading: "A carregar…",
  ob_title: "OFERTA GUARDIAN",
  ob_save: "GUARDAR OFERTA",
  ob_customer_offer: "Cliente e oferta",
  ob_hours_travel: "Horas e viagem",
  ob_breakdown: "Detalhe (do backend)",
  ob_items: "Linhas",
  ob_add_line: "+ Adicionar linha",
  ob_remove: "Remover",
  ob_saved: "Oferta guardada",
  ob_select_client: "Escolhe cliente...",
  ob_select_first: "Seleciona um cliente primeiro",
};

const it: Strings = {
  nav_offers: "Offerte Guardian",
  nav_customers: "Clienti",
  cust_title: "Clienti (F0)",
  cust_id_ph: "SAP Debitor ID (customer_id)",
  cust_name_ph: "Nome account",
  cust_country_ph: "Paese (facoltativo)",
  cust_create: "Crea",
  cust_loading: "Caricamento…",
  ob_title: "OFFERTA GUARDIAN",
  ob_save: "SALVA OFFERTA",
  ob_customer_offer: "Cliente e offerta",
  ob_hours_travel: "Ore e viaggio",
  ob_breakdown: "Dettaglio (dal backend)",
  ob_items: "Righe",
  ob_add_line: "+ Aggiungi riga",
  ob_remove: "Rimuovi",
  ob_saved: "Offerta salvata",
  ob_select_client: "Seleziona cliente...",
  ob_select_first: "Seleziona prima un cliente",
};

export const STRINGS: Record<Lang, Strings> = { es, en, de, pt, it };

export function t(lang: Lang, key: keyof Strings): string {
  return STRINGS[lang][key];
}
