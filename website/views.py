from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from . import db
from .models import Accommodation, Booking
from .forms import AccommodationForm
import os
from datetime import date, datetime, timedelta
from werkzeug.utils import secure_filename

# Convert date range to easier to read format by reducing redundant information
def format_date_range(start_date, end_date):
    # If year is the same, don't show year
    if start_date.year == end_date.year:
        # If month is the same, don't show month range
        if start_date.month == end_date.month:
            # If day is the same, show only the day
            if start_date.day == end_date.day:
                return start_date.strftime('%B %d')
            # If day is different, show day range
            else:
                return f"{start_date.strftime('%B')} {start_date.day}-{end_date.day}"
        # If month is different, show month range
        else:
            return f"{start_date.strftime('%B')} {start_date.day} - {end_date.strftime('%B')} {end_date.day}"
    # If year is different, show full date range
    else:
        return f"{start_date.strftime('%B')} {start_date.day}, {start_date.year} - {end_date.strftime('%B')} {end_date.day}, {end_date.year}"

views = Blueprint('views', __name__)

# ---Home/Profile Page---
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    today = date.today()
    # Sort bookings by upcoming > (cancelled | already finished), in descending order of id (by latest first)
    user_bookings = sorted(
        current_user.bookings,
        key=lambda b: (
            b.cancelled or (b.start_date + timedelta(days=b.nights) < today),
            b.start_date if not b.cancelled and (b.start_date + timedelta(days=b.nights) >= today) else -b.id
        )
    )
    # Sort accommodations in descending order of id (by latest first)
    user_accommodations = sorted(
        Accommodation.query.filter_by(
            owner_id=current_user.id,
            is_deleted=False
        ).all(),
        key=lambda a: a.id,
        reverse=True
    )
    return render_template("home.html", user=current_user, bookings=user_bookings, accommodations=user_accommodations, timedelta=timedelta)

# ---Create Accommodation Page---
@views.route('/create-accommodation', methods=['GET', 'POST'])
@login_required
def create_accommodation():
    form = AccommodationForm()
    if form.validate_on_submit():
        # Create accommodation instance
        new_accommodation = Accommodation(
            owner_id=current_user.id,
            name=form.name.data,
            address=form.address.data,
            description=form.description.data,
            tags=form.tags.data,
            price=form.price.data,
            guests_limit=form.guests_limit.data,
            available_start_date=form.available_start_date.data,
            available_end_date=form.available_end_date.data
        )
        # Commit here first before adding the images because we need the accommodation id
        db.session.add(new_accommodation)
        db.session.commit()
        
        # Save images to the accommodation's folder
        if form.images.data:
            image_folder = os.path.join('website', 'static', 'images', str(new_accommodation.id))
            os.makedirs(image_folder, exist_ok=True)
            image_filenames = []
            for index, image in enumerate(form.images.data):
                if image and hasattr(image, 'save'):
                    image_filename = secure_filename(datetime.now().strftime('%Y%m%d%H%M%S') + '_' + str(index) + '.jpg')
                    image.save(os.path.join(image_folder, image_filename))
                    image_filenames.append(image_filename)
            new_accommodation.images = ','.join(image_filenames)
            db.session.commit()
        
        flash('Accommodation created successfully!', category='success')
        return redirect(url_for('views.home'))
    
    return render_template('create_accommodation.html', form=form, user=current_user)

# ---Edit Accommodation Page---
@views.route('/edit-accommodation/<int:accommodation_id>', methods=['GET', 'POST'])
@login_required
def edit_accommodation(accommodation_id):
    accommodation = Accommodation.query.get_or_404(accommodation_id)

    # Check if the user has permission to edit the accommodation
    if accommodation.owner_id != current_user.id:
        flash('You do not have permission to edit this accommodation.', category='error')
        return redirect(url_for('views.accommodation_detail', accommodation_id=accommodation_id))
    
    # Check if the accommodation has already been deleted
    if accommodation.is_deleted:
        flash('This accommodation has already been deleted and cannot be edited anymore.', category='error')
        return redirect(url_for('views.home', accommodation_id=accommodation_id))
    
    today = date.today()
    form = AccommodationForm(obj=accommodation)
    
    # Handle form submission
    if request.method == 'POST':
        # Handle update request
        if request.form.get('form_name') == 'update_form' and form.validate_on_submit():
            # Check for bookings that will be affected by the updated date range and have not yet finished
            affected_bookings = []
            for booking in Booking.query.filter(Booking.accommodation_id == accommodation_id, Booking.cancelled == False).all():
                booking_end_date = booking.start_date + timedelta(days=booking.nights)
                if (booking.start_date < form.available_start_date.data or booking_end_date > form.available_end_date.data) and booking_end_date > today:
                    affected_bookings.append(booking)

            # If there are affected bookings and confirmation is not provided, return a warning
            if affected_bookings and 'confirmed' not in request.form:
                return jsonify({
                    'status': 'warning',
                    'message': 'There are existing bookings that fall outside the updated date range. These bookings will be refunded if you proceed.'
                }), 400

            # Update accommodation details
            accommodation.name = form.name.data
            accommodation.address = form.address.data
            accommodation.description = form.description.data
            accommodation.tags = form.tags.data
            accommodation.price = form.price.data
            accommodation.guests_limit = form.guests_limit.data
            accommodation.available_start_date = form.available_start_date.data
            accommodation.available_end_date = form.available_end_date.data

            # Cancel affected bookings if confirmation is provided
            if affected_bookings and 'confirmed' in request.form:
                for booking in affected_bookings:
                    booking.cancelled = True
                    # for improvement, if payment logic is implemented, refund the booking here

            # Handle image updates
            image_folder = os.path.join('website', 'static', 'images', str(accommodation.id))
            os.makedirs(image_folder, exist_ok=True)
            kept_images = request.form.get('kept_images').split(',') if request.form.get('kept_images') else []
            original_images = accommodation.images.split(',') if accommodation.images else []
            removed_images = set(original_images) - set(kept_images)
            # Remove images that are not kept
            for image_filename in removed_images:
                image_path = os.path.join(image_folder, image_filename)
                if os.path.exists(image_path):
                    os.remove(image_path)
            # Add new images
            if 'new_images' in request.files:
                new_images = request.files.getlist('new_images')
                new_image_filenames = []
                for index, image in enumerate(new_images):
                    if image:
                        image_filename = secure_filename(datetime.now().strftime('%Y%m%d%H%M%S') + '_' + str(index) + '.jpg')
                        image.save(os.path.join(image_folder, image_filename))
                        new_image_filenames.append(image_filename)
                accommodation.images = ','.join(kept_images + new_image_filenames)
            else:
                accommodation.images = ','.join(kept_images)

            db.session.commit()
            
            flash('Accommodation updated successfully!', category='success')
            return redirect(url_for('views.accommodation_detail', accommodation_id=accommodation.id))

        # Handle delete request
        if request.form.get('form_name') == 'delete_form':
            # Check bookings that will be affected by the deletion
            active_bookings = []
            for booking in Booking.query.filter(Booking.accommodation_id == accommodation_id, Booking.cancelled == False).all():
                booking_end_date = booking.start_date + timedelta(days=booking.nights)
                if booking_end_date > today:
                    active_bookings.append(booking) # only append bookings that have not yet finished

            # If there are active bookings
            if active_bookings:
                for booking in active_bookings:
                    booking.cancelled = True
                    # for improvement, if payment logic is implemented, refund the booking here

            accommodation.is_deleted = True
            
            db.session.commit()

            flash('Accommodation deleted successfully.', category='success')
            return redirect(url_for('views.home'))

    return render_template('edit_accommodation.html', user=current_user, form=form, accommodation=accommodation)

# ---Accommodations Page---
@views.route('/accommodations')
def accommodations():
    # Get all accommodations that are not deleted, in descending order of id (by latest first)
    all_accommodations = Accommodation.query.filter_by(is_deleted=False).order_by(Accommodation.id.desc()).all()
    return render_template('accommodations.html', accommodations=all_accommodations, user=current_user)

@views.route('/accommodation/<int:accommodation_id>')
def accommodation_detail(accommodation_id):
    accommodation = Accommodation.query.get_or_404(accommodation_id)
    
    # Check if the accommodation has already been deleted
    if accommodation.is_deleted:
        flash('This accommodation has already been deleted and cannot be viewed anymore.', category='error')
        return redirect(url_for('views.accommodations'))
    
    today = date.today()
    # Set default check-in date to either today or the accommodation's available start date, whichever is later
    default_check_in_date = max(today, accommodation.available_start_date.date())
    # Set default check-out date to be 4 days after the default check-in date (e.g. 16 Jan -> 20 Jan)
    default_check_out_date = default_check_in_date + timedelta(days=5)
    return render_template('accommodation_detail.html', accommodation=accommodation, user=current_user, now=datetime.now(), default_check_in_date=default_check_in_date, default_check_out_date=default_check_out_date, timedelta=timedelta)

# ---Book Accommodation Function---
@views.route('/book-accommodation/<int:accommodation_id>', methods=['POST'])
@login_required
def book_accommodation(accommodation_id):
    service_fee_percentage = 0.10
    
    accommodation = Accommodation.query.get_or_404(accommodation_id)
    check_in_date = datetime.strptime(request.form.get('check_in_date'), '%Y-%m-%d').date()
    check_out_date = datetime.strptime(request.form.get('check_out_date'), '%Y-%m-%d').date()
    nights = (check_out_date - check_in_date).days
    guests_str = request.form.get('guests', '0')
    try:
        guests = int(guests_str)
    except ValueError:
        flash('Invalid number of guests.', category='error')
        return redirect(url_for('views.accommodation_detail', accommodation_id=accommodation_id))
    
    # Check if the accommodation has already been deleted
    if accommodation.is_deleted:
        flash('This accommodation has already been deleted and cannot be booked anymore.', category='error')
        return redirect(url_for('views.accommodations'))
    
    # Limit to accommodation's available dates
    if check_in_date < accommodation.available_start_date.date() or check_out_date > accommodation.available_end_date.date():
        flash('Requested dates are not available for booking.', category='error')
        return redirect(url_for('views.accommodation_detail', accommodation_id=accommodation_id))
    
    # Limit check-out date to not be before or equal to check-in date
    if check_out_date <= check_in_date:
        flash('Check-out date must be after check-in date.', category='error')
        return redirect(url_for('views.accommodation_detail', accommodation_id=accommodation_id))
    
    # Limit number of guests to be at least 1 (if there is limit) and not exceed the accommodation's limit
    if (accommodation.guests_limit > 1 and guests < 1) or guests > accommodation.guests_limit:
        flash(f'Number of guests must be between 1 and {accommodation.guests_limit}.', category='error')
        return redirect(url_for('views.accommodation_detail', accommodation_id=accommodation_id))

    # Check for overlaps with existing bookings
    overlapping_bookings = Booking.query.filter(
        Booking.accommodation_id == accommodation_id,
        Booking.start_date < check_out_date,
        Booking.cancelled == False  # Exclude cancelled bookings
    ).all()
    
    for booking in overlapping_bookings:
        booking_end_date = booking.start_date + timedelta(days=booking.nights)
        if booking_end_date > check_in_date:
            flash('The requested dates overlap with an existing booking.', category='error')
            return redirect(url_for('views.accommodation_detail', accommodation_id=accommodation_id))

    booking_price = accommodation.price * nights
    service_fee = booking_price * service_fee_percentage
    total_price = booking_price + service_fee

    # Create booking instance
    new_booking = Booking(
        accommodation_id=accommodation_id,
        user_id=current_user.id,
        start_date=check_in_date,
        nights=nights,
        price=total_price,
    )

    db.session.add(new_booking)
    db.session.commit()

    # for improvement, if payment logic is implemented, process the payment here
    
    flash('Booking successful!', category='success')
    return redirect(url_for('views.home', accommodation_id=accommodation_id))

# ---Cancel Booking Function---
@views.route('/cancel-booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    # Make sure the user owns the booking
    if booking.user_id != current_user.id:
        flash('You do not have permission to cancel this booking.', category='error')
        return redirect(url_for('views.home'))
    
    # Too late to cancel booking after one day from the start date
    if datetime.now().date() >= (booking.start_date + timedelta(days=1)):
        flash('It is too late to cancel this booking.', category='error')
        return redirect(url_for('views.home'))

    booking.cancelled = True
    
    db.session.commit()

    # for improvement, if payment logic is implemented, refund the booking here

    flash('Booking cancelled successfully.', category='success')
    return redirect(url_for('views.home'))