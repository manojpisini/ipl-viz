"""
Every IPL venue mapped to its physical dimensions and lat/lon.

Multiple Cricsheet name variants alias into the same Stadium instance,
so `resolve_stadium()` in `match_context.py` can do exact-key lookups
without fuzzy matching for the vast majority of matches.
"""
from engine.stadium import Stadium

# -- Major home grounds -------------------------------------------------------

S_BANGALORE = Stadium(
    name="M. Chinnaswamy Stadium", location="Bengaluru, India",
    width_m=131.8, length_m=133.7, straight_boundary_m=72.5, square_boundary_m=62.5,
    lat=12.9788, lon=77.5996,
)
S_KOLKATA = Stadium(
    name="Eden Gardens", location="Kolkata, India",
    width_m=136.5, length_m=141.0, straight_boundary_m=77.0, square_boundary_m=67.0,
    lat=22.5646, lon=88.3433,
)
S_MUMBAI_W = Stadium(
    name="Wankhede Stadium", location="Mumbai, India",
    width_m=134.0, length_m=152.0, straight_boundary_m=76.0, square_boundary_m=65.0,
    lat=18.9389, lon=72.8258,
)
S_DELHI = Stadium(
    name="Arun Jaitley Stadium", location="Delhi, India",
    width_m=130.0, length_m=138.0, straight_boundary_m=68.0, square_boundary_m=65.0,
    lat=28.6379, lon=77.2432,
)
S_CHENNAI = Stadium(
    name="MA Chidambaram Stadium", location="Chennai, India",
    width_m=135.0, length_m=145.0, straight_boundary_m=75.0, square_boundary_m=68.0,
    lat=13.0628, lon=80.2793,
)
S_AHMEDABAD = Stadium(
    name="Narendra Modi Stadium", location="Ahmedabad, India",
    width_m=150.0, length_m=160.0, straight_boundary_m=75.0, square_boundary_m=70.0,
    lat=23.0905, lon=72.5976,
)
S_HYDERABAD = Stadium(
    name="Rajiv Gandhi International Stadium", location="Hyderabad, India",
    width_m=145.0, length_m=155.0, straight_boundary_m=75.0, square_boundary_m=68.0,
    lat=17.4065, lon=78.5505,
)
S_JAIPUR = Stadium(
    name="Sawai Mansingh Stadium", location="Jaipur, India",
    width_m=150.0, length_m=156.0, straight_boundary_m=78.0, square_boundary_m=72.0,
    lat=26.8940, lon=75.8032,
)
S_MOHALI = Stadium(
    name="PCA IS Bindra Stadium", location="Mohali, India",
    width_m=145.0, length_m=158.0, straight_boundary_m=78.0, square_boundary_m=73.0,
    lat=30.6911, lon=76.7377,
)
S_LUCKNOW = Stadium(
    name="Ekana Cricket Stadium", location="Lucknow, India",
    width_m=156.0, length_m=160.0, straight_boundary_m=77.5, square_boundary_m=67.5,
    lat=26.8123, lon=81.0247,
)

# -- Secondary / historical Indian venues -------------------------------------

S_MULLANPUR = Stadium(
    name="Maharaja Yadavindra Singh Stadium", location="Mullanpur, India",
    width_m=132.0, length_m=148.0, straight_boundary_m=74.0, square_boundary_m=65.5,
    lat=30.8170, lon=76.7680,
)
S_CHANDIGARH = Stadium(
    name="Maharaja Yadavindra Singh Stadium", location="Mullanpur, India",
    width_m=132.0, length_m=148.0, straight_boundary_m=74.0, square_boundary_m=65.5,
    lat=30.8170, lon=76.7680,
)
S_VIZAG = Stadium(
    name="ACA-VDCA Cricket Stadium", location="Visakhapatnam, India",
    width_m=135.0, length_m=145.0, straight_boundary_m=74.0, square_boundary_m=68.0,
    lat=17.7974, lon=83.3510,
)
S_DHARAMSHALA = Stadium(
    name="HPCA Stadium", location="Dharamshala, India",
    width_m=128.0, length_m=140.0, straight_boundary_m=70.0, square_boundary_m=64.0,
    lat=32.1976, lon=76.3260,
)
S_GUWAHATI = Stadium(
    name="Barsapara Cricket Stadium", location="Guwahati, India",
    width_m=130.0, length_m=145.0, straight_boundary_m=74.0, square_boundary_m=65.0,
    lat=26.1437, lon=91.7375,
)
S_RANCHI = Stadium(
    name="JSCA International Stadium", location="Ranchi, India",
    width_m=145.0, length_m=150.0, straight_boundary_m=75.0, square_boundary_m=70.0,
    lat=23.3080, lon=85.2760,
)
S_RAJKOT = Stadium(
    name="Saurashtra Cricket Association Stadium", location="Rajkot, India",
    width_m=140.0, length_m=145.0, straight_boundary_m=70.0, square_boundary_m=68.0,
    lat=22.3686, lon=70.7302,
)
S_INDORE = Stadium(
    name="Holkar Cricket Stadium", location="Indore, India",
    width_m=120.0, length_m=135.0, straight_boundary_m=68.0, square_boundary_m=56.0,
    lat=22.7247, lon=75.8753,
)
S_PUNE = Stadium(
    name="Maharashtra Cricket Association Stadium", location="Pune, India",
    width_m=145.0, length_m=150.0, straight_boundary_m=74.0, square_boundary_m=68.0,
    lat=18.6740, lon=73.7064,
)
S_NAVI_MUMBAI = Stadium(
    name="DY Patil Stadium", location="Navi Mumbai, India",
    width_m=140.0, length_m=155.0, straight_boundary_m=78.0, square_boundary_m=68.0,
    lat=19.0435, lon=73.0238,
)
S_MUMBAI_B = Stadium(
    name="Brabourne Stadium", location="Mumbai, India",
    width_m=130.0, length_m=140.0, straight_boundary_m=72.0, square_boundary_m=66.0,
    lat=18.9322, lon=72.8252,
)
S_CUTTACK = Stadium(
    name="Barabati Stadium", location="Cuttack, India",
    width_m=135.0, length_m=140.0, straight_boundary_m=70.0, square_boundary_m=65.0,
    lat=20.4811, lon=85.8675,
)
S_RAIPUR = Stadium(
    name="Shaheed Veer Narayan Singh Stadium", location="Raipur, India",
    width_m=145.0, length_m=150.0, straight_boundary_m=75.0, square_boundary_m=68.0,
    lat=21.1944, lon=81.7865,
)
S_NAGPUR = Stadium(
    name="VCA Stadium, Jamtha", location="Nagpur, India",
    width_m=145.0, length_m=150.0, straight_boundary_m=76.0, square_boundary_m=70.0,
    lat=21.0145, lon=79.0375,
)
S_KANPUR = Stadium(
    name="Green Park", location="Kanpur, India",
    width_m=135.0, length_m=140.0, straight_boundary_m=70.0, square_boundary_m=65.0,
    lat=26.4820, lon=80.3475,
)

# -- UAE venues (2014, 2020, 2021 bio-bubble seasons) -------------------------

S_DUBAI = Stadium(
    name="Dubai International Cricket Stadium", location="Dubai, UAE",
    width_m=140.0, length_m=148.0, straight_boundary_m=74.0, square_boundary_m=70.0,
    lat=25.0458, lon=55.2172,
)
S_ABU_DHABI = Stadium(
    name="Sheikh Zayed Cricket Stadium", location="Abu Dhabi, UAE",
    width_m=145.0, length_m=155.0, straight_boundary_m=76.0, square_boundary_m=70.0,
    lat=24.3965, lon=54.5450,
)
S_SHARJAH = Stadium(
    name="Sharjah Cricket Stadium", location="Sharjah, UAE",
    width_m=130.0, length_m=124.0, straight_boundary_m=62.0, square_boundary_m=65.0,
    lat=25.3308, lon=55.4199,
)

# -- South Africa (2009 season) -----------------------------------------------

S_JOHANNESBURG = Stadium(
    name="Wanderers Stadium", location="Johannesburg, SA",
    width_m=150.0, length_m=155.0, straight_boundary_m=78.0, square_boundary_m=72.0,
    lat=-26.1319, lon=28.0577,
)
S_CENTURION = Stadium(
    name="SuperSport Park", location="Centurion, SA",
    width_m=145.0, length_m=150.0, straight_boundary_m=75.0, square_boundary_m=70.0,
    lat=-25.8603, lon=28.1963,
)
S_DURBAN = Stadium(
    name="Kingsmead", location="Durban, SA",
    width_m=140.0, length_m=145.0, straight_boundary_m=72.0, square_boundary_m=68.0,
    lat=-29.8504, lon=31.0298,
)
S_GQEBERHA = Stadium(
    name="St George's Park", location="Gqeberha, SA",
    width_m=145.0, length_m=150.0, straight_boundary_m=75.0, square_boundary_m=70.0,
    lat=-33.9631, lon=25.6111,
)
S_CAPETOWN = Stadium(
    name="Newlands", location="Cape Town, SA",
    width_m=142.0, length_m=148.0, straight_boundary_m=74.0, square_boundary_m=68.0,
    lat=-33.9702, lon=18.4682,
)
S_KIMBERLEY = Stadium(
    name="De Beers Diamond Oval", location="Kimberley, SA",
    width_m=140.0, length_m=145.0, straight_boundary_m=70.0, square_boundary_m=65.0,
    lat=-28.7479, lon=24.7766,
)
S_BLOEMFONTEIN = Stadium(
    name="OUTsurance Oval", location="Bloemfontein, SA",
    width_m=140.0, length_m=145.0, straight_boundary_m=72.0, square_boundary_m=68.0,
    lat=-29.1171, lon=26.2081,
)
S_EAST_LONDON = Stadium(
    name="Buffalo Park", location="East London, SA",
    width_m=135.0, length_m=140.0, straight_boundary_m=68.0, square_boundary_m=62.0,
    lat=-33.0033, lon=27.9175,
)

# -- Venue-string → Stadium mapping ------------------------------------------
# Multiple Cricsheet name variants map here so exact-key lookup almost always works.

STADIUMS_BY_VENUE = {
    # India core
    "M. Chinnaswamy Stadium":                                S_BANGALORE,
    "M Chinnaswamy Stadium":                                 S_BANGALORE,
    "Eden Gardens":                                          S_KOLKATA,
    "Wankhede Stadium":                                      S_MUMBAI_W,
    "Arun Jaitley Stadium":                                  S_DELHI,
    "Feroz Shah Kotla":                                      S_DELHI,
    "MA Chidambaram Stadium":                                S_CHENNAI,
    "MA Chidambaram Stadium, Chepauk":                       S_CHENNAI,
    "MA Chidambaram Stadium, Chepauk, Chennai":              S_CHENNAI,

    # India expansion
    "Narendra Modi Stadium":                                 S_AHMEDABAD,
    "Sardar Patel Stadium, Motera":                          S_AHMEDABAD,
    "Rajiv Gandhi International Stadium":                    S_HYDERABAD,
    "Rajiv Gandhi International Stadium, Uppal":             S_HYDERABAD,
    "Rajiv Gandhi International Stadium Uppal":              S_HYDERABAD,
    "Sawai Mansingh Stadium":                                S_JAIPUR,
    "PCA IS Bindra Stadium":                                 S_MOHALI,
    "Punjab Cricket Association Stadium, Mohali":            S_MOHALI,
    "Punjab Cricket Association IS Bindra Stadium, Mohali":  S_MOHALI,
    "Punjab Cricket Association IS Bindra Stadium Mohali":   S_MOHALI,
    "Ekana Cricket Stadium":                                 S_LUCKNOW,
    "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium": S_LUCKNOW,
    "Maharaja Yadavindra Singh Stadium":                     S_CHANDIGARH,
    "Maharaja Yadavindra Singh International Cricket Stadium, Mullanpur": S_MULLANPUR,
    "Maharaja Yadavindra Singh International Cricket Stadium, New Chandigarh": S_CHANDIGARH,

    # India secondary
    "ACA-VDCA Cricket Stadium":                              S_VIZAG,
    "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium":  S_VIZAG,
    "HPCA Stadium":                                          S_DHARAMSHALA,
    "Himachal Pradesh Cricket Association Stadium":           S_DHARAMSHALA,
    "Barsapara Cricket Stadium":                             S_GUWAHATI,
    "JSCA International Stadium":                            S_RANCHI,
    "JSCA International Stadium Complex":                    S_RANCHI,
    "Saurashtra Cricket Association Stadium":                S_RAJKOT,
    "Holkar Cricket Stadium":                                S_INDORE,
    "DY Patil Stadium":                                      S_NAVI_MUMBAI,
    "Dr DY Patil Sports Academy":                            S_NAVI_MUMBAI,
    "Maharashtra Cricket Association Stadium":               S_PUNE,
    "Subrata Roy Sahara Stadium":                            S_PUNE,
    "Brabourne Stadium":                                     S_MUMBAI_B,
    "Barabati Stadium":                                      S_CUTTACK,
    "Shaheed Veer Narayan Singh International Stadium":      S_RAIPUR,
    "Vidarbha Cricket Association Stadium, Jamtha":           S_NAGPUR,
    "Green Park":                                            S_KANPUR,
    "Nehru Stadium":                                         S_KANPUR,

    # UAE
    "Dubai International Cricket Stadium":                   S_DUBAI,
    "Sheikh Zayed Cricket Stadium":                          S_ABU_DHABI,
    "Sheikh Zayed Stadium":                                  S_ABU_DHABI,
    "Sharjah Cricket Stadium":                               S_SHARJAH,

    # South Africa
    "Wanderers Stadium":                                     S_JOHANNESBURG,
    "New Wanderers Stadium":                                 S_JOHANNESBURG,
    "Centurion Park":                                        S_CENTURION,
    "SuperSport Park":                                       S_CENTURION,
    "Kingsmead":                                             S_DURBAN,
    "Kingsmead Cricket Ground":                              S_DURBAN,
    "St George's Park":                                      S_GQEBERHA,
    "Newlands":                                              S_CAPETOWN,
    "Newlands Cricket Ground":                               S_CAPETOWN,
    "De Beers Diamond Oval":                                 S_KIMBERLEY,
    "Buffalo Park":                                          S_EAST_LONDON,
    "OUTsurance Oval":                                       S_BLOEMFONTEIN,
}