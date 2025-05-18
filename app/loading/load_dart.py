import io
import os
import re
import zipfile
import requests

import pandas as pd


def load_current_dart_stock_code(stock_code_only: bool = True) -> pd.DataFrame:
    "DART에서 제공하는 회사의 리스트를 조회하는 함수입니다."

    token = os.environ["DART_TOKEN"]
    base_url = "https://opendart.fss.or.kr/api/corpCode.xml"
    full_url = f"{base_url}?crtfc_key={token}"
    response = requests.get(full_url)

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        with z.open("CORPCODE.xml") as f:
            lines = [l.decode() for l in f.readlines()]
        data_xml = "\n".join(lines)
        stock_code_df = pd.read_xml(io.StringIO(data_xml))

    if stock_code_only:
        stock_code_df = stock_code_df[stock_code_df.stock_code != " "]

    stock_code_df["corp_code"] = stock_code_df.corp_code.apply(
        lambda code: (8 - len(str(code))) * "0" + str(code)
    )
    stock_code_df.reset_index(drop=True, inplace=True)

    return stock_code_df


def load_dart_report(
    corp_code: str,
    year: int,
    quarter: str,
) -> pd.DataFrame:
    "DART에서 제공하는 정기보고서 재무재표를 조회하는 함수입니다."

    reprt_code = {
        "1Q": "11013",
        "2Q": "11012",
        "3Q": "11014",
        "4Q": "11011",
    }
    token = os.environ["DART_TOKEN"]
    base_url = "https://opendart.fss.or.kr/api/fnlttSinglAcnt.xml"
    full_url = (
        f"{base_url}?crtfc_key={token}"
        + f"&corp_code={corp_code}&bsns_year={year}&reprt_code={reprt_code[quarter]}"
    )
    response = requests.get(full_url)
    xml_str = response.content.decode()
    m = re.search(r"<status>(.*?)</status>", xml_str, re.S)
    status_code = m.group(1).strip()
    status = {
        "000": "정상",
        "010": "등록되지 않은 키입니다.",
        "011": "사용할 수 없는 키입니다.",
        "012": "접근할 수 없는 IP입니다.",
        "013": "조회된 데이타가 없습니다.",
        "014": "파일이 존재하지 않습니다.",
        "020": "요청 제한을 초과하였습니다.",
        "021": "조회 가능한 회사 개수가 초과하였습니다.(최대 100건)",
        "100": "필드의 부적절한 값입니다.",
        "101": "부적절한 접근입니다.",
        "800": "시스템 점검으로 인한 서비스가 중지 중입니다.",
        "900": "정의되지 않은 오류가 발생하였습니다.",
        "901": "사용자 계정의 개인정보 보유기간이 만료되어 사용할 수 없는 키입니다.",
    }
    if status_code == "000":
        report_data_raw = pd.read_xml(io.StringIO(xml_str))
        report_data = report_data_raw.pivot_table(
            index="fs_nm",
            columns="account_nm",
            values="thstrm_amount",
            aggfunc="sum",
        ).dropna()

        for col in report_data.columns:
            report_data[col] = report_data[col].apply(
                lambda value: int(str(value).replace(",", "")) if value != "-" else None
            )
        report_data.reset_index(inplace=True)
        report_data.insert(0, "quarter", quarter)
        report_data.insert(0, "year", year)
        report_data.insert(0, "corp_code", corp_code)

    else:
        print("corp code: ", corp_code)
        print("error code: ", status_code)
        print("error message: ", status[status_code])
        report_data = pd.DataFrame()

    return report_data


if __name__ == "__main__":
    load_dart_report(
        corp_code="00186939",
        year=2025,
        quarter="1Q",
    )
