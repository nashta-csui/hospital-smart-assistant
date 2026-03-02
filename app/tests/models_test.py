from datetime import date, datetime, time
from operator import eq
from uuid import UUID

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.base.base_model import Base
from app.models.base.dokter import Dokter
from app.models.base.jadwal_praktik import JadwalPraktik
from app.models.base.pasien import JenisKelamin, Pasien
from app.models.base.sesi_konsultasi import SesiKonsultasi, StatusSesiKonsultasi

# Berikut adalah test case yang mencakup skenario yang kemungkinan
# sering ditanyakan oleh pasien

# 1. Keluhan -> Jadwal Terdekat -> Spesialisasi (Positive)
# User query: "Saya sedang tidak enak badan. Berikut keluhan saya. Tolong cari jadwal
# terdekat yang tersedia"
# Expected query:
#   SELECT * FROM jadwal_praktik
#   JOIN dokter ON jadwal_praktik.dokter_id = dokter.id
#   WHERE dokter.spesialisasi = 'kardiovaskuler'

stmt1 = (
    select(JadwalPraktik)
    .join(Dokter, JadwalPraktik.dokter_id == Dokter.id)
    .where(eq(Dokter.spesialisasi, "kardiovaskuler"))
)

# 2. Keluhan -> Jadwal Untuk N Hari Ke Depan -> Spesialisasi & Kuota (Positive)
# User query: "Saya ingin melakukan pemeriksaan medis rutin. Tolong carikan jadwal luang
# untuk satu bulan ke depan untuk dokter umum"
# Expected query:
#   SELECT * FROM jadwal_praktik
#   JOIN dokter ON jadwal_praktik.dokter_id = dokter.id
#   LEFT JOIN sesi_konsultasi ON jadwal_praktik.id = sesi_konsultasi.jadwal_id
#   WHERE dokter.spesialisasi = 'umum'
#   GROUP BY jadwal_praktik.id
#   HAVING jadwal_praktik.kuota_harian > COUNT(sesi_konsultasi.id)

# Subquery untuk menghitung jumlah sesi yang sudah di-book per jadwal
subq_booked_count = (
    select(func.count(SesiKonsultasi.id))
    .where(SesiKonsultasi.jadwal_id == JadwalPraktik.id)
    .correlate(JadwalPraktik)
    .scalar_subquery()
)

stmt2 = (
    select(JadwalPraktik)
    .join(Dokter, JadwalPraktik.dokter_id == Dokter.id)
    .where(eq(Dokter.spesialisasi, "umum"))
    .where(JadwalPraktik.kuota_harian > func.coalesce(subq_booked_count, 0))
)

# 3. Pencarian Dokter Spesifik -> Cek Ketersediaan (Positive)
# User query: "Apakah Dokter Asep Sutisna ada jadwal praktek yang buka minggu ini?"
# Expected query:
#   SELECT * FROM jadwal_praktik
#   JOIN dokter ON jadwal_praktik.dokter_id = dokter.id
#   WHERE dokter.nama ILIKE '%Asep Sutisna%'
#   AND jadwal_praktik.is_available = TRUE

stmt3 = (
    select(JadwalPraktik)
    .join(Dokter, JadwalPraktik.dokter_id == Dokter.id)
    .where(Dokter.nama.ilike("%Asep Sutisna%"))
    .where(JadwalPraktik.is_available.is_(True))
)

# 4. Cek Status Janji Temu Saya (Positive)
# User query: "Bagaimana status janji temu saya dengan Dokter Budi?"
# Note: Asumsi kita memiliki ID pasien dari konteks auth (misal: 'user_uuid')
# Expected query:
#   SELECT sesi_konsultasi.* FROM sesi_konsultasi
#   JOIN jadwal_praktik ON ...
#   JOIN dokter ON ...
#   WHERE pasien_id = 'user_uuid' AND dokter.nama ILIKE '%Budi%'

# Placeholder UUID untuk simulasi user yang sedang login
current_user_id = UUID("00000000-0000-0000-0000-000000000000")

stmt4 = (
    select(SesiKonsultasi)
    .join(JadwalPraktik, SesiKonsultasi.jadwal_id == JadwalPraktik.id)
    .join(Dokter, JadwalPraktik.dokter_id == Dokter.id)
    .where(SesiKonsultasi.pasien_id == current_user_id)
    .where(Dokter.nama.ilike("%Budi%"))
)

# 5. Filter Jadwal Berdasarkan Hari Spesifik (Positive)
# User query: "Saya hanya bisa datang hari Sabtu. Tolong carikan dokter gigi yang praktek hari itu."
# Expected query:
#   SELECT * FROM jadwal_praktik
#   JOIN dokter ON ...
#   WHERE dokter.spesialisasi = 'gigi'
#   AND jadwal_praktik.hari_dalam_minggu = 6 (Sabtu)

stmt5 = (
    select(JadwalPraktik)
    .join(Dokter, JadwalPraktik.dokter_id == Dokter.id)
    .where(eq(Dokter.spesialisasi, "gigi"))
    .where(eq(JadwalPraktik.hari_dalam_minggu, 6))
)

# ==========================================
# TEST CONFIGURATION & FIXTURES
# ==========================================


@pytest.fixture(name="session")
def session_fixture():
    """
    Buat sebuah temporary in-memory database menggunakan SQLite
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(engine)


@pytest.fixture(name="test_data")
def test_data_fixture(session):
    """
    Seeding database untuk memeriksa kebenaran dari test case di atas
    """
    # == Dokter ==
    dr_cardio = Dokter(
        nama="Dr. Heart",
        spesialisasi="kardiovaskuler",
        no_telepon="+628111111",
        email="heart@hospital.com",
        password_hash="secret",
        is_active=True,
    )
    dr_umum = Dokter(
        nama="Dr. Strange",
        spesialisasi="umum",
        no_telepon="+628222222",
        email="strange@hospital.com",
        password_hash="secret",
        is_active=True,
    )
    dr_asep = Dokter(
        nama="Dr. Asep Sutisna",
        spesialisasi="bedah",
        no_telepon="+628333333",
        email="asep@hospital.com",
        password_hash="secret",
        is_active=True,
    )
    dr_budi = Dokter(
        nama="Dr. Budi Santoso",
        spesialisasi="anak",
        no_telepon="+628444444",
        email="budi@hospital.com",
        password_hash="secret",
        is_active=True,
    )
    dr_gigi = Dokter(
        nama="Dr. Tooth",
        spesialisasi="gigi",
        no_telepon="+628555555",
        email="tooth@hospital.com",
        password_hash="secret",
        is_active=True,
    )

    session.add_all([dr_cardio, dr_umum, dr_asep, dr_budi, dr_gigi])
    session.commit()

    # == JadwalPraktik ==

    # Schedule for Dr. Cardio (Target for stmt1)
    jadwal_cardio = JadwalPraktik(
        dokter_id=dr_cardio.id,
        hari_dalam_minggu=1,  # Senin
        jam_mulai=time(9, 0),
        jam_selesai=time(12, 0),
        kuota_harian=10,
        is_available=True,
    )

    # Schedule for Dr. Umum (Target for stmt2 - Available)
    jadwal_umum_open = JadwalPraktik(
        dokter_id=dr_umum.id,
        hari_dalam_minggu=2,  # Selasa
        jam_mulai=time(10, 0),
        jam_selesai=time(14, 0),
        kuota_harian=5,  # High quota
        is_available=True,
    )

    # Schedule for Dr. Umum (Target for stmt2 - Full)
    jadwal_umum_full = JadwalPraktik(
        dokter_id=dr_umum.id,
        hari_dalam_minggu=3,  # Rabu
        jam_mulai=time(10, 0),
        jam_selesai=time(14, 0),
        kuota_harian=1,  # Only 1 slot
        is_available=True,
    )

    # Schedule for Dr. Asep (Target for stmt3)
    jadwal_asep = JadwalPraktik(
        dokter_id=dr_asep.id,
        hari_dalam_minggu=4,  # Kamis
        jam_mulai=time(13, 0),
        jam_selesai=time(17, 0),
        kuota_harian=5,
        is_available=True,
    )

    # Schedule for Dr. Budi (Target for stmt4)
    jadwal_budi = JadwalPraktik(
        dokter_id=dr_budi.id,
        hari_dalam_minggu=5,  # Jumat
        jam_mulai=time(8, 0),
        jam_selesai=time(11, 0),
        kuota_harian=5,
        is_available=True,
    )

    # Schedule for Dr. Gigi (Target for stmt5 - Saturday)
    jadwal_gigi_sabtu = JadwalPraktik(
        dokter_id=dr_gigi.id,
        hari_dalam_minggu=6,  # Sabtu (Target)
        jam_mulai=time(9, 0),
        jam_selesai=time(15, 0),
        kuota_harian=5,
        is_available=True,
    )

    session.add_all(
        [
            jadwal_cardio,
            jadwal_umum_open,
            jadwal_umum_full,
            jadwal_asep,
            jadwal_budi,
            jadwal_gigi_sabtu,
        ]
    )
    session.commit()

    # == Pasien dan Konsultasi ==

    # Create the patient that matches 'current_user_id' from the code above
    pasien_saya = Pasien(
        id=current_user_id,
        nomor_rekam_medis="RM-001",
        nik="1234567890123456",
        nama="Saya Pasien",
        no_telepon="+62899999",
        jenis_kelamin=JenisKelamin.L,
        tanggal_lahir=date(1990, 1, 1),
        alamat="Jl. Sehat",
        email="saya@pasien.com",
        password_hash="hashed",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    session.add(pasien_saya)
    session.commit()

    # Create a Consultation for "Dr. Budi" (Target for stmt4)
    sesi_budi = SesiKonsultasi(
        pasien_id=pasien_saya.id,
        jadwal_id=jadwal_budi.id,
        tanggal_kunjungan=date.today(),
        nomor_antrean="A-1",
        keluhan="Demam",
        status=StatusSesiKonsultasi.BOOKED,
        created_at=datetime.now(),
    )

    # Create a Consultation that FILLS the quota for jadwal_umum_full (Target for stmt2 logic)
    sesi_umum_full = SesiKonsultasi(
        pasien_id=pasien_saya.id,
        jadwal_id=jadwal_umum_full.id,
        tanggal_kunjungan=date.today(),
        nomor_antrean="B-1",
        keluhan="Checkup",
        status=StatusSesiKonsultasi.BOOKED,  # Taking the only slot
        created_at=datetime.now(),
    )

    session.add_all([sesi_budi, sesi_umum_full])
    session.commit()

    return {
        "dr_cardio": dr_cardio,
        "jadwal_cardio": jadwal_cardio,
        "jadwal_umum_open": jadwal_umum_open,
        "jadwal_asep": jadwal_asep,
        "sesi_budi": sesi_budi,
        "jadwal_gigi_sabtu": jadwal_gigi_sabtu,
    }


# ==========================================
# TEST CASES
# ==========================================


def test_stmt1_keluhan_spesialisasi(session, test_data):
    """
    Test Query 1: Find schedule for 'kardiovaskuler'.
    Expected: Should return Dr. Heart's schedule.
    """
    result = session.execute(stmt1).scalars().all()

    assert len(result) == 1
    assert result[0].id == test_data["jadwal_cardio"].id
    assert result[0].dokter.nama == "Dr. Heart"


def test_stmt2_future_schedule_with_quota(session, test_data):
    """
    Test Query 2: Find 'umum' schedule with available quota.
    Expected: Should return 'jadwal_umum_open' (quota 5, booked 0).
              Should NOT return 'jadwal_umum_full' (quota 1, booked 1).
    """
    result = session.execute(stmt2).scalars().all()

    # We expect only the open schedule, not the full one
    assert len(result) == 1
    assert result[0].id == test_data["jadwal_umum_open"].id
    assert result[0].dokter.nama == "Dr. Strange"


def test_stmt3_search_doctor_by_name(session, test_data):
    """
    Test Query 3: Find schedule for doctor name like 'Asep Sutisna'.
    Expected: Should return Dr. Asep's schedule.
    """
    result = session.execute(stmt3).scalars().all()

    assert len(result) >= 1
    assert result[0].id == test_data["jadwal_asep"].id
    assert "Asep" in result[0].dokter.nama


def test_stmt4_my_appointment_status(session, test_data):
    """
    Test Query 4: Find my appointment with 'Dr. Budi'.
    Expected: Should return the specific SesiKonsultasi record.
    """
    result = session.execute(stmt4).scalars().all()

    assert len(result) == 1
    assert result[0].id == test_data["sesi_budi"].id
    assert result[0].keluhan == "Demam"


def test_stmt5_filter_day_saturday(session, test_data):
    """
    Test Query 5: Find 'gigi' doctor on Saturday (index 6).
    Expected: Should return Dr. Tooth's schedule.
    """
    result = session.execute(stmt5).scalars().all()

    assert len(result) == 1
    assert result[0].id == test_data["jadwal_gigi_sabtu"].id
    assert result[0].hari_dalam_minggu == 6
