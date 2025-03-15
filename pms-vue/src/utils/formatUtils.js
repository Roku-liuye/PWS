import dayjs from 'dayjs'

export const formatDateTime = (time) => {
  return time ? dayjs(time).format('YYYY-MM-DD HH:mm:ss') : ''
}