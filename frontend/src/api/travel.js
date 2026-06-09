import { get, post } from "./http";

export const travelApi = {
  getAttractions: () => get("/attractions/"),
  getRoutes: () => get("/routes/"),
  getBookings: () => get("/bookings/"),
  getNotices: () => get("/notifications/"),
  createBooking: (payload) => post("/bookings/", payload),
};
