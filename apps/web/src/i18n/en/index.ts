import audit from './audit.json'
import auth from './auth.json'
import common from './common.json'
import community from './community.json'
import dashboard from './dashboard.json'
import demo from './demo.json'
import discipline from './discipline.json'
import finance from './finance.json'
import governance from './governance.json'
import membership from './membership.json'
import search from './search.json'

const catalogs: Array<Record<string, string>> = [
  common,
  auth,
  dashboard,
  search,
  membership,
  finance,
  governance,
  discipline,
  community,
  audit,
  demo,
]

export const en: Record<string, string> = Object.assign({}, ...catalogs)
