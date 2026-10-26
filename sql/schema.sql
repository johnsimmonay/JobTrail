CREATE TABLE applications (
    id            INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    company_name  VARCHAR(100) NOT NULL,
    job_title     VARCHAR(100) NOT NULL,
    applied_date  DATE NOT NULL DEFAULT CURRENT_DATE,
    status        TEXT NOT NULL DEFAULT 'applied' CHECK (status IN ('applied', 'interview', 'offer', 'rejected')),
    source        TEXT,
    job_url       TEXT,
    notes         TEXT,
    location      TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);