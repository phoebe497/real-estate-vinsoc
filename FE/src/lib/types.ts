export type SubdivisionSummary = {
  slug: string;
  name: string;
  introduction: string;
  handover_status: string;
  thumbnail_url: string | null;
};

export type ApartmentSpec = {
  unit_type: string;
  area_note: string | null;
  price_note: string | null;
};

export type Amenity = {
  name: string;
  scope: "internal" | "external";
  description: string | null;
};

export type SalesPolicy = {
  id: number;
  title: string;
  policy_content: string;
  status: string;
};

export type SubdivisionDetail = SubdivisionSummary & {
  location: string;
  apartment_specs: ApartmentSpec[];
  amenities: Amenity[];
  sales_policies: SalesPolicy[];
};
